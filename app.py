import streamlit as st
from pathlib import Path

from src.config.settings import settings
from src.models.schemas import Document, MessageRole, ChatMessage
from src.utils.helpers import is_pdf, validate_file_size
from src.ingestion.pipeline import ingest_document
from src.generation.rag_chain import ask_question
from src.generation.llm_client import check_ollama_health


UPLOADS = Path(settings.uploads_path)
UPLOADS.mkdir(parents=True, exist_ok=True)


def save_upload(uploaded_file) -> Path:
	dest = UPLOADS / uploaded_file.name
	with dest.open("wb") as fh:
		fh.write(uploaded_file.getbuffer())
	return dest


def main():
	st.set_page_config(page_title="RAG Tutor", layout="wide")

	# Initialize session state
	if "documents" not in st.session_state:
		st.session_state.documents = []
	if "messages" not in st.session_state:
		st.session_state.messages = []
	if "ollama_ok" not in st.session_state:
		st.session_state.ollama_ok = False
	if "conversation_session" not in st.session_state:
		from uuid import uuid4
		from src.models.schemas import ConversationSession, Subject
		st.session_state.conversation_session = ConversationSession(session_id=f"sess-{uuid4().hex[:8]}")
	if "subjects" not in st.session_state:
		from src.models.schemas import Subject
		st.session_state.subjects = []
	if "current_subject" not in st.session_state:
		st.session_state.current_subject = None

	# Sidebar: Ollama health check
	st.sidebar.title("RAG Tutor")

	health = check_ollama_health()
	if health.get("ok"):
		st.sidebar.success("✅ Ollama Running")
		st.session_state.ollama_ok = True
	else:
		st.sidebar.error("❌ Ollama Not Running")
		st.sidebar.markdown("""
			**To get started:**
			1. Start Ollama: `ollama serve`
			2. Pull models: `ollama pull llama3.2 nomic-embed-text llama-guard3:1b`
		""")

	# Sidebar: Subject management
	st.sidebar.markdown("---")
	st.sidebar.subheader("📚 Subjects")

	col1, col2 = st.sidebar.columns([3, 1])
	with col1:
		new_subject = st.text_input("New subject:")
	with col2:
		if st.button("Add", key="add_subject_btn"):
			if new_subject and new_subject not in [s.name for s in st.session_state.subjects]:
				from src.models.schemas import Subject
				st.session_state.subjects.append(Subject(name=new_subject))
				st.rerun()

	if st.session_state.subjects:
		subject_names = [s.name for s in st.session_state.subjects]
		current_idx = subject_names.index(st.session_state.current_subject) if st.session_state.current_subject in subject_names else 0
		st.session_state.current_subject = st.sidebar.selectbox(
			"Select subject:",
			subject_names,
			index=current_idx,
		)
	else:
		st.sidebar.info("Create a subject to get started")

	# Sidebar: Document upload
	st.sidebar.markdown("---")
	st.sidebar.subheader("📄 Materials")

	if st.session_state.current_subject:
		uploaded = st.sidebar.file_uploader("Upload PDF", type=["pdf"], accept_multiple_files=True)
		if uploaded:
			for f in uploaded:
				# Skip if already uploaded/processed in this session
				if any(d.file_name == f.name for d in st.session_state.documents):
					st.sidebar.info(f"{f.name} already uploaded")
					continue
				# Save and validate
				path = save_upload(f)
				err = validate_file_size(path, settings.max_file_size_mb)
				if err:
					st.sidebar.error(err)
					continue
				if not is_pdf(path):
					st.sidebar.error("Uploaded file is not a PDF")
					continue

				with st.sidebar.spinner("Processing upload..."):
					doc = ingest_document(path, file_name=path.name)
					doc.subject = st.session_state.current_subject

					# Add collection to subject
					current_subj = next((s for s in st.session_state.subjects if s.name == st.session_state.current_subject), None)
					if current_subj and doc.collection_name:
						current_subj.collection_names.append(doc.collection_name)

					st.session_state.documents.append(doc)
	else:
		st.sidebar.info("Create a subject first to upload materials")

	# Sidebar: Document list (filtered by subject)
	st.sidebar.markdown("---")
	subject_docs = [d for d in st.session_state.documents if d.subject == st.session_state.current_subject] if st.session_state.current_subject else []
	for d in subject_docs:
		status = getattr(d, "status", "PENDING")
		pages = getattr(d, "total_pages", None)

		# Status emoji
		status_emoji = {
			"PENDING": "⏳",
			"PROCESSING": "🔄",
			"READY": "✅",
			"FAILED": "❌",
		}.get(status, "❓")

		label = f"{status_emoji} {d.file_name}"
		if pages:
			label += f" ({pages} pages)"

		if status == "FAILED" and d.error_message:
			st.sidebar.error(label + f"\n{d.error_message}")
		elif status == "READY":
			st.sidebar.success(label)
		else:
			st.sidebar.write(label)

	# Main content
	st.title("📚 RAG Tutor")
	if st.session_state.current_subject:
		st.info(f"📍 Currently studying: **{st.session_state.current_subject}**")
	else:
		st.info("📍 Select or create a subject to begin")

	# Display chat history
	for msg in st.session_state.messages:
		with st.chat_message(msg.role.value):
			st.markdown(msg.content)
			if msg.citations:
				st.caption(f"Based on {len(msg.citations)} source(s)")

	# Chat input (subject-scoped)
	ready_docs = [d for d in subject_docs if d.status.value == "READY"]

	if not ready_docs:
		st.info("📤 Upload course materials to get started!")
		return

	if ready_docs and st.session_state.ollama_ok:
		user_input = st.chat_input("Ask a question about the materials...")

		if user_input:
			# Add user message to history
			user_msg = ChatMessage(role=MessageRole.USER, content=user_input)
			st.session_state.messages.append(user_msg)

			# Display user message
			with st.chat_message("user"):
				st.markdown(user_input)

			# Generate response
			with st.chat_message("assistant"):
				with st.spinner("Thinking..."):
					# Get collection names from ready documents
					collection_names = [d.collection_name for d in ready_docs if d.collection_name]

					# Generate answer
					assistant_msg = ask_question(
						query=user_input,
						collection_names=collection_names,
						history=st.session_state.messages[:-1],  # Exclude the user message just added
					)

					# Add to history
					st.session_state.messages.append(assistant_msg)

					# Display response
					st.markdown(assistant_msg.content)
	else:
		if not st.session_state.ollama_ok:
			st.error("Please start Ollama to enable chat.")


if __name__ == "__main__":
	main()

