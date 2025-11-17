"""
Mini Cloud-Drive System
A lightweight cloud-based file storage system using Firebase and Streamlit
"""

import streamlit as st
from file_storage import FileStorageManager, MAX_FILE_SIZE_MB
from firebase_config import initialize_firebase
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Mini Cloud-Drive",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #1f77b4;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Firebase
@st.cache_resource
def init_firebase():
    """Initialize Firebase (cached to run once)"""
    try:
        initialize_firebase()
        return True
    except Exception as e:
        st.error(f"Failed to initialize Firebase: {str(e)}")
        return False

# Initialize the file storage manager
@st.cache_resource
def get_storage_manager():
    """Get FileStorageManager instance (cached)"""
    return FileStorageManager()

def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

def main():
    """Main application function"""

    # Header
    st.markdown('<div class="main-header">☁️ Mini Cloud-Drive</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Lightweight Cloud File Storage System</div>', unsafe_allow_html=True)

    # Initialize Firebase
    if not init_firebase():
        st.stop()

    # Get storage manager
    storage_manager = get_storage_manager()

    # Sidebar
    with st.sidebar:
        st.header("📊 Storage Statistics")

        stats = storage_manager.get_storage_stats()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-number">{stats['total_files']}</div>
                    <div class="stat-label">Total Files</div>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-number">{stats['total_size_mb']}</div>
                    <div class="stat-label">Total Size (MB)</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info(
            f"""
            **Features:**
            - Upload files up to {MAX_FILE_SIZE_MB} MB
            - Cloud-based storage
            - Metadata tracking
            - Download links
            - Real-time sync

            **Tech Stack:**
            - Frontend: Streamlit
            - Storage: Firebase Storage
            - Database: Firestore
            """
        )

    # Main content area
    tab1, tab2 = st.tabs(["📤 Upload Files", "📁 My Files"])

    # Upload Tab
    with tab1:
        st.subheader("Upload Your Files")
        st.write(f"Maximum file size: **{MAX_FILE_SIZE_MB} MB**")

        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=None,  # Accept all file types
            help=f"Upload files up to {MAX_FILE_SIZE_MB} MB"
        )

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            upload_button = st.button("🚀 Upload to Cloud", type="primary", use_container_width=True)

        if uploaded_file is not None:
            # Display file info
            st.write("**File Details:**")
            file_info_col1, file_info_col2 = st.columns(2)
            with file_info_col1:
                st.write(f"- **Name:** {uploaded_file.name}")
                st.write(f"- **Size:** {format_file_size(uploaded_file.size)}")
            with file_info_col2:
                st.write(f"- **Type:** {uploaded_file.type}")

            # Upload button action
            if upload_button:
                with st.spinner("Uploading file to cloud..."):
                    result = storage_manager.upload_file(uploaded_file)

                    if result['success']:
                        st.success("✅ File uploaded successfully!")

                        # Display upload details
                        with st.expander("📋 Upload Details", expanded=True):
                            metadata = result['metadata']
                            st.write(f"**Original Name:** {metadata['original_name']}")
                            st.write(f"**Stored Name:** {metadata['stored_name']}")
                            st.write(f"**Size:** {metadata['size_mb']} MB")
                            st.write(f"**Storage Path:** `{metadata['storage_path']}`")
                            st.write(f"**Download URL:** [Click here]({metadata['download_url']})")

                        # Refresh stats
                        st.rerun()
                    else:
                        st.error(f"❌ Upload failed: {result['error']}")
        else:
            if upload_button:
                st.warning("⚠️ Please select a file first")

    # My Files Tab
    with tab2:
        st.subheader("Your Uploaded Files")

        # Refresh button
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()

        # Get all files
        files = storage_manager.get_all_files()

        if not files:
            st.info("📭 No files uploaded yet. Upload your first file in the 'Upload Files' tab!")
        else:
            st.write(f"**Total Files:** {len(files)}")

            # Create DataFrame for better display
            file_data = []
            for f in files:
                file_data.append({
                    'File Name': f['original_name'],
                    'Size': format_file_size(f['size_bytes']),
                    'Type': f['mime_type'] or 'Unknown',
                    'Uploaded': f['uploaded_at'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(f['uploaded_at'], datetime) else str(f['uploaded_at']),
                    'Storage Path': f['storage_path'],
                    'Download URL': f['download_url']
                })

            df = pd.DataFrame(file_data)

            # Display as interactive table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Download URL": st.column_config.LinkColumn("Download URL", display_text="Download")
                }
            )

            # Detailed view
            st.markdown("---")
            st.subheader("📄 File Details")

            for idx, file in enumerate(files):
                with st.expander(f"📎 {file['original_name']}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Original Name:** {file['original_name']}")
                        st.write(f"**Stored Name:** {file['stored_name']}")
                        st.write(f"**Size:** {file['size_mb']} MB ({format_file_size(file['size_bytes'])})")
                        st.write(f"**MIME Type:** {file['mime_type'] or 'Unknown'}")

                    with col2:
                        st.write(f"**Storage Path:** `{file['storage_path']}`")
                        st.write(f"**Document ID:** `{file['id']}`")
                        uploaded_time = file['uploaded_at']
                        if isinstance(uploaded_time, datetime):
                            st.write(f"**Uploaded:** {uploaded_time.strftime('%Y-%m-%d %H:%M:%S')}")
                        else:
                            st.write(f"**Uploaded:** {uploaded_time}")

                    # Download button
                    st.markdown(f"[🔗 Download File]({file['download_url']})")

                    # Delete button (optional)
                    if st.button(f"🗑️ Delete", key=f"delete_{file['id']}"):
                        with st.spinner("Deleting file..."):
                            delete_result = storage_manager.delete_file(file['id'], file['storage_path'])
                            if delete_result['success']:
                                st.success("File deleted successfully!")
                                st.rerun()
                            else:
                                st.error(f"Failed to delete: {delete_result['error']}")

if __name__ == "__main__":
    main()
