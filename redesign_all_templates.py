import os
import glob
import re

# =========================================================================================
# STITCH AI TAILWIND CSS INTEGRATION
# This script automates migrating legacy Django HTML templates to the new Stitch AI Design.
# It performs 2 main functions:
# 1. Wraps the main layout in a modern, shadow-border Stitch AI UI Card.
# 2. Replaces legacy CSS classes (like Bootstrap) with custom Tailwind utility classes.
# =========================================================================================

# The main layout wrappers for the application content block
STITCH_CARD_START = '\n<div class="max-w-[1440px] mx-auto w-full px-4 md:px-8 py-8"><div class="bg-white border border-black p-8 md:p-12 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">\n'
STITCH_CARD_END = '\n</div></div>\n'

# Class mapping from legacy standard names to the bold Stitch Tailwind design language
CSS_CLASS_MAPPING = {
    "btn btn-primary": "flex min-w-[84px] cursor-pointer items-center justify-center border border-black bg-black text-white hover:bg-white hover:text-black transition-colors h-10 px-6 text-sm font-bold uppercase tracking-wide",
    "btn btn-secondary": "flex min-w-[84px] cursor-pointer items-center justify-center border border-black hover:bg-black hover:text-white transition-colors h-10 px-6 text-black text-sm font-bold uppercase tracking-wide",
    "btn btn-danger": "flex min-w-[84px] cursor-pointer items-center justify-center border border-red-600 hover:bg-red-600 hover:text-white text-red-600 transition-colors h-10 px-6 text-sm font-bold uppercase tracking-wide",
    "btn btn-outline-secondary": "flex cursor-pointer items-center justify-center border border-gray-300 hover:border-black hover:bg-gray-50 text-black transition-colors h-10 px-4 text-xs font-bold uppercase tracking-wide w-full",
    "form-control": "w-full h-12 bg-transparent border-b border-gray-300 text-black placeholder:text-gray-400 px-4 focus:outline-none focus:border-black transition-colors text-sm font-mono tracking-wide",
    'class="card"': 'class="bg-white border border-black p-6 group hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all duration-300"',
    "card-title": "text-xl font-bold text-black uppercase tracking-widest mb-2",
    "card-text": "text-sm text-gray-600 font-light mb-4",
    '<h1': '<h1 class="text-black tracking-tight text-3xl md:text-5xl font-light font-display uppercase mb-6" ',
    '<h2': '<h2 class="text-2xl font-light uppercase tracking-tight mb-4" ',
}

def inject_stitch_design(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    modified = False

    # 1. Substitute utility classes
    for old_class, new_class in CSS_CLASS_MAPPING.items():
        if isinstance(old_class, str) and '="' in old_class:
            # specifically targeting 'class="something"' matching
            if old_class in content:
                content = content.replace(old_class, new_class)
                modified = True
        else:
            # Targeting the interior of a class attribute
            search_str = f'class="{old_class}"'
            replace_str = f'class="{new_class}"'
            if search_str in content:
                content = content.replace(search_str, replace_str)
                modified = True
            
            # Additional check for naked HTML tags like <h1> replacing correctly
            if old_class.startswith('<h') and old_class in content:
                content = content.replace(old_class + '>', new_class + '>')
                modified = True

    # 2. Wrap layout blocks
    if 'max-w-[1440px]' not in content and '{% block content %}' in content:
        # Avoid wrapping completely custom pages or pages that don't extend base.html
        if 'extends "base.html"' in content or "extends 'base.html'" in content:
            # Inject STITCH_CARD_START after {% block content %}
            content, count_start = re.subn(r'({%\s*block\s+content\s*%})', r'\1' + STITCH_CARD_START, content)
            # Inject STITCH_CARD_END before {% endblock %}
            content, count_end = re.subn(r'({%\s*endblock\s*%})', STITCH_CARD_END + r'\1', content)
            
            if count_start > 0 and count_end > 0:
                modified = True

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

if __name__ == "__main__":
    search_dirs = [
        "accounts/templates", "adminapp/templates", "core/templates", 
        "ecommerce/templates", "messenger/templates", "notes/templates",
        "notifications/templates", "papers/templates", "roadmaps/templates",
        "social/templates", "university/templates", "videocall/templates"
    ]
    
    # We skip files that are fully bespoke Stitch AI outputs (already handled)
    skip_files = [
        "roadmap_list.html", "paper_view.html", "chat_room.html", "lobby.html"
    ]
    
    updated_count = 0
    print("Starting Stitch AI CSS deployment across all generic templates...")
    
    for dir_path in search_dirs:
        for file_path in glob.glob(f"{dir_path}/**/*.html", recursive=True):
            if any(skip in file_path for skip in skip_files):
                continue
            
            if inject_stitch_design(file_path):
                updated_count += 1
                print(f"-> Redesigned: {file_path}")
                
    print(f"\n✅ SUCCESSFULLY DEPLOYED: {updated_count} HTML templates updated to the Stitch AI Design System.")
