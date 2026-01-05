import streamlit as st
import requests
import json
import time
from pathlib import Path
import os
import sys

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger import get_logger

logger = get_logger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Multimodal RAG Use Case Generator",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e86c1;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def check_api_status():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_system_status():
    """Get system status from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def index_documents():
    """Index documents via API"""
    try:
        response = requests.post(f"{API_BASE_URL}/index", timeout=60)
        if response.status_code == 200:
            return response.json()
        return {"error": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def upload_file(file):
    """Upload a file via API"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=30)
        if response.status_code == 200:
            return response.json()
        return {"error": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def generate_use_cases(query, debug_mode=False):
    """Generate use cases via API"""
    try:
        payload = {"query": query, "debug_mode": debug_mode}
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json=payload,
            timeout=120
        )
        if response.status_code == 200:
            return response.json()
        return {"error": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def main():
    st.markdown('<div class="main-header"> Multimodal RAG Use Case Generator</div>', unsafe_allow_html=True)

    # Check API status
    api_running = check_api_status()

    if not api_running:
        st.error(" API server is not running. Please start it first!")
        st.warning("To start the API server, run: `cd src && python main.py`")
        st.info(" You can also run the demo without the API: `cd src && python demo.py`")

        # Show basic info even without API
        st.markdown('<div class="section-header">ℹ System Information</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Sample Documents")
            st.code("""
data/input/
├── authentication_system.md
└── payment_system.md
            """)

        with col2:
            st.markdown("###  Quick Commands")
            st.code("""
# Run demo (no API needed)
cd src && python demo.py

# Start API server
cd src && python main.py

# Start UI (after API)
cd src && streamlit run ui.py
            """)

        return
        st.header(" System Control")

        # API Status
        api_running = check_api_status()
        if api_running:
            st.success(" API Server: Running")
        else:
            st.error(" API Server: Not Running")
            st.warning("Please start the API server with: `cd src && python main.py`")

        # System Status
        if api_running:
            status = get_system_status()
            if status:
                st.subheader(" System Status")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Indexed Chunks", status.get("indexed_chunks", 0))
                with col2:
                    st.metric("Status", status.get("status", "unknown").title())

        st.divider()

        # Quick Actions
        st.subheader(" Quick Actions")
        if st.button(" Refresh Status", use_container_width=True):
            st.rerun()

        if st.button("Index Documents", use_container_width=True, disabled=not api_running):
            with st.spinner("Indexing documents..."):
                result = index_documents()
                if "error" in result:
                    st.error(f"Indexing failed: {result['error']}")
                else:
                    st.success(f" Indexed {result['files_processed']} files into {result['total_chunks']} chunks")
                    time.sleep(1)
                    st.rerun()

    # Main content
    if not api_running:
        st.error(" API server is not running. Please start it first!")
        st.code("cd src && python main.py", language="bash")
        return

    tab1, tab2, tab3, tab4 = st.tabs([" Upload", " Generate", "Results", "ℹ About"])

    with tab1:
        st.markdown('<div class="section-header"> Upload Documents</div>', unsafe_allow_html=True)

        st.markdown("Upload documents to be indexed for use case generation. Supported formats: PDF, TXT, MD, CSV, JSON, images, etc.")

        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "txt", "md", "csv", "json", "yaml", "yml", "png", "jpg", "jpeg", "docx"],
            help="Select a document file to upload"
        )

        if uploaded_file is not None:
            st.success(f" Selected: {uploaded_file.name}")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(" Upload & Index", use_container_width=True):
                    with st.spinner("Uploading file..."):
                        result = upload_file(uploaded_file)
                        if result.get("error"):
                            st.error(f"Upload failed: {result.get('error')}")
                        else:
                            st.success(f"✅ {result['message']}")

                            # Auto-index after upload
                            with st.spinner("Indexing uploaded file..."):
                                index_result = index_documents()
                                if not index_result.get("error"):
                                    st.success("✅ File indexed successfully!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.warning("File uploaded but indexing may have failed")

    with tab2:
        st.markdown('<div class="section-header"> Generate Use Cases</div>', unsafe_allow_html=True)

        st.markdown("Enter a query to generate test cases and use cases based on the indexed documents.")

        query = st.text_area(
            "Query",
            placeholder="e.g., Generate test cases for user authentication and payment processing",
            height=100,
            help="Describe what kind of use cases or test cases you want to generate"
        )

        col1, col2 = st.columns([3, 1])
        with col1:
            debug_mode = st.checkbox("Debug Mode", help="Show additional debugging information")
        with col2:
            generate_button = st.button(" Generate", use_container_width=True, disabled=not query.strip())

        if generate_button and query.strip():
            with st.spinner("Generating use cases... This may take a moment."):
                result = generate_use_cases(query, debug_mode)

                if result.get("error"):
                    st.error(f"Generation failed: {result.get('error')}")
                else:
                    # Store result in session state for the Results tab
                    st.session_state.last_result = result
                    st.session_state.last_query = query

                    st.success(" Use cases generated successfully!")

                    # Show summary
                    use_cases = result.get("use_cases", [])
                    confidence = result.get("confidence_score", 0)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Use Cases Generated", len(use_cases))
                    with col2:
                        st.metric("Confidence Score", f"{confidence:.2f}")
                    with col3:
                        st.metric("Sources Used", len(result.get("retrieved_sources", [])))

                    # Show warnings if any
                    warnings = result.get("warnings", [])
                    if warnings:
                        with st.expander(" Warnings", expanded=True):
                            for warning in warnings:
                                st.warning(warning)

                    # Show assumptions if any
                    assumptions = result.get("assumptions", [])
                    if assumptions:
                        with st.expander(" Assumptions Made", expanded=True):
                            for assumption in assumptions:
                                st.info(assumption)

                    st.info("Check the 'Results' tab for detailed output")

    with tab3:
        st.markdown('<div class="section-header"> Generation Results</div>', unsafe_allow_html=True)

        if "last_result" not in st.session_state:
            st.info("No results yet. Generate some use cases first!")
            return

        result = st.session_state.last_result
        query = st.session_state.last_query

        st.markdown(f"**Query:** {query}")

        use_cases = result.get("use_cases", [])

        if not use_cases:
            st.warning("No use cases were generated.")
            return

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Use Cases", len(use_cases))
        with col2:
            st.metric("Confidence", f"{result.get('confidence_score', 0):.2f}")
        with col3:
            st.metric("Sources", len(result.get("retrieved_sources", [])))
        with col4:
            st.metric("Grounding Score", f"{result.get('grounding_score', 0):.2f}")

        # Use cases
        for i, uc in enumerate(use_cases, 1):
            with st.expander(f" Use Case {i}: {uc.get('title', 'Untitled')}", expanded=i<=3):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**Goal:** {uc.get('goal', 'N/A')}")
                    st.markdown(f"**Preconditions:** {', '.join(uc.get('preconditions', []))}")

                    # Test data
                    test_data = uc.get('test_data', {})
                    if test_data:
                        st.markdown("**Test Data:**")
                        for key, value in test_data.items():
                            st.code(f"{key}: {value}", language="text")

                with col2:
                    st.markdown("**Steps:**")
                    steps = uc.get('steps', [])
                    for step in steps:
                        st.markdown(f"{step['step_number']}. {step['action']}")
                        st.caption(f"Expected: {step['expected_result']}")

                # Expected results
                expected = uc.get('expected_results', [])
                if expected:
                    st.markdown("**Expected Results:**")
                    for exp in expected:
                        st.success(exp)

                # Negative cases
                negative = uc.get('negative_cases', [])
                if negative:
                    st.markdown("**Negative Test Cases:**")
                    for neg in negative:
                        st.error(neg)

                # Boundary cases
                boundary = uc.get('boundary_cases', [])
                if boundary:
                    st.markdown("**Boundary Test Cases:**")
                    for bound in boundary:
                        st.warning(bound)

        # Sources
        sources = result.get("retrieved_sources", [])
        if sources:
            with st.expander(" Sources Used"):
                for source in sources:
                    st.code(source)

        # Debug info
        if result.get("debug_info"):
            with st.expander(" Debug Information"):
                debug = result["debug_info"]
                st.json(debug)

    with tab4:
        st.markdown('<div class="section-header">ℹ About</div>', unsafe_allow_html=True)

        st.markdown("""
        ## Multimodal RAG Use Case Generator

        This application uses Retrieval-Augmented Generation (RAG) to automatically generate
        comprehensive test cases and use cases from your documents.

        ### Features

        - **Multimodal Processing**: Supports text, PDF, images, and data files
        - ** Smart Retrieval**: Hybrid search combining vector similarity and keyword matching
        - ** Quality Guards**: Confidence checking, hallucination detection, and input validation
        - ** Fast Generation**: Powered by Groq's LLaMA models
        - ** Beautiful UI**: Streamlit-based interface for easy interaction

        ### How to Use

        1. **Upload Documents**: Add your requirements, specifications, or documentation
        2. **Index Content**: Process and index the documents for retrieval
        3. **Generate Use Cases**: Enter queries to generate test cases and scenarios
        4. **Review Results**: Examine generated use cases with confidence scores

        ### Supported File Types

        - Text: `.txt`, `.md`
        - Documents: `.pdf`, `.docx`
        - Data: `.csv`, `.json`, `.yaml`
        - Images: `.png`, `.jpg`, `.jpeg` (with OCR)

        ### Architecture

        ```
        Documents → Ingestion → Vector Store → Retrieval → Generation → Use Cases
        ```

        Built with FastAPI backend and Streamlit frontend.
        """)

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Quick Start")
            st.code("""
# 1. Start the API server
cd src && python main.py

# 2. Start the UI (in another terminal)
cd src && streamlit run ui.py
            """)

        with col2:
            st.markdown("###  API Endpoints")
            st.code("""
GET  /         - Health check
POST /index    - Index documents
POST /upload   - Upload file
POST /generate - Generate use cases
GET  /status   - System status
            """)

if __name__ == "__main__":
    main()