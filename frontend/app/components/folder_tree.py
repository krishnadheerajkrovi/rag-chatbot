"""
Folder tree component for organizing chats and documents
"""
import streamlit as st
import requests


def render_folder_tree(folders, selected_folder_id, on_folder_select, api_base_url, headers):
    """Render a hierarchical folder tree"""
    
    # Organize folders by parent
    root_folders = [f for f in folders if f.get('parent_folder_id') is None]
    
    for folder in root_folders:
        render_folder_item(folder, folders, selected_folder_id, on_folder_select, api_base_url, headers, level=0)


def render_folder_item(folder, all_folders, selected_folder_id, on_folder_select, api_base_url, headers, level=0):
    """Render a single folder item with its children"""
    indent = "  " * level
    folder_id = folder['id']
    folder_name = folder['name']
    
    # Check if this folder is selected
    is_selected = folder_id == selected_folder_id
    
    # Folder button with selection state
    col1, col2, col3 = st.columns([0.7, 2, 0.3])
    
    with col1:
        # Expand/collapse button for folders with children
        children = [f for f in all_folders if f.get('parent_folder_id') == folder_id]
        if children:
            if st.button("📁", key=f"expand_{folder_id}"):
                pass  # Toggle expand state
    
    with col2:
        button_type = "primary" if is_selected else "secondary"
        if st.button(f"{indent}📂 {folder_name}", key=f"folder_{folder_id}", type=button_type, use_container_width=True):
            on_folder_select(folder_id)
    
    with col3:
        # Delete folder button
        if st.button("🗑️", key=f"del_folder_{folder_id}", help="Delete folder"):
            try:
                response = requests.delete(
                    f"{api_base_url}/folders/{folder_id}",
                    headers=headers
                )
                if response.status_code == 200:
                    st.success(f"Deleted folder: {folder_name}")
                    st.rerun()
                else:
                    st.error("Failed to delete folder")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Render children (recursive)
    children = [f for f in all_folders if f.get('parent_folder_id') == folder_id]
    for child in children:
        render_folder_item(child, all_folders, selected_folder_id, on_folder_select, api_base_url, headers, level + 1)


def create_folder_dialog(api_base_url, headers, parent_folder_id=None):
    """Dialog for creating a new folder"""
    with st.form("create_folder_form"):
        folder_name = st.text_input("Folder Name", placeholder="e.g., Work Projects")
        folder_description = st.text_area("Description (optional)")
        submit = st.form_submit_button("Create Folder")
        
        if submit and folder_name:
            try:
                data = {
                    "name": folder_name,
                    "description": folder_description
                }
                if parent_folder_id:
                    data["parent_folder_id"] = parent_folder_id
                
                response = requests.post(
                    f"{api_base_url}/folders/",
                    json=data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    st.success(f"Created folder: {folder_name}")
                    st.rerun()
                else:
                    st.error(f"Failed to create folder: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
