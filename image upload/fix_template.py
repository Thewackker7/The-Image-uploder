import os

path = r"d:\django\projects\image upload\templates\core\index.html"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Look for the broken line. We'll use a regex-like approach or exact match if we can find it.
# The previous view showed it was split.
import re

# This pattern tries to match the p tag with the date filter even if split
pattern = re.compile(r'<p class="text-gray-500 text-\[9px\] uppercase font-bold mt-0\.5">\{\{ post\.created_at\|date:"F d, Y\s+H:i" \}\}</p>', re.DOTALL)
new_line = '<p class="text-gray-500 text-[9px] uppercase font-bold mt-0.5">{{ post.created_at|date:"F d, Y H:i" }}</p>'

fixed_content = pattern.sub(new_line, content)

if fixed_content == content:
    print("Pattern not found with regex, trying simpler match...")
    # Alternative: just replace the specific part we saw split
    search_str = '{{ post.created_at|date:"F d, Y\n                            H:i" }}'
    fixed_content = content.replace(search_str, '{{ post.created_at|date:"F d, Y H:i" }}')

if fixed_content != content:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    print("File updated successfully.")
else:
    print("Could not find the target string to replace.")
    # Let's print a small chunk around where we expect it to be
    idx = content.find('post.created_at')
    if idx != -1:
        print("Found 'post.created_at' at index", idx)
        print("Context:", repr(content[idx-50:idx+100]))
