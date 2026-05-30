import os

root_dir = r"C:\Users\ambat\Documents\Codex\2026-05-18\files-mentioned-by-the-user-multi\trading_system"
output_file = r"C:\Users\ambat\Documents\Codex\2026-05-18\files-mentioned-by-the-user-multi\trading_system\TRADING_SYSTEM_FULL_CODEBASE.md"

exclude_dirs = {
    "venv", ".venv", "__pycache__", ".git", "node_modules", "logs", "dist", ".github"
}
exclude_extensions = {
    ".db", ".pyc", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2", ".ttf", ".eot", ".exe", ".bin"
}
exclude_files = {
    "package-lock.json", ".token_key", "NTUSER.DAT", "ntuser.dat.LOG1", "ntuser.dat.LOG2"
}

with open(output_file, "w", encoding="utf-8") as f_out:
    f_out.write("# TRADING SYSTEM FULL CODEBASE DUMP\n\n")
    f_out.write(f"Generated on: {os.popen('date /t').read().strip()} {os.popen('time /t').read().strip()}\n")
    f_out.write("Root Directory: " + root_dir + "\n\n")
    
    for root, dirs, files in os.walk(root_dir):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in exclude_extensions or file in exclude_files:
                continue
            
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, root_dir)
            
            f_out.write(f"\n--- START FILE: {relative_path} ---\n")
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f_in:
                    content = f_in.read()
                    f_out.write(content)
            except Exception as e:
                f_out.write(f"[ERROR READING FILE: {e}]")
            f_out.write(f"\n--- END FILE: {relative_path} ---\n")

print(f"Aggregation complete. Output saved to: {output_file}")
