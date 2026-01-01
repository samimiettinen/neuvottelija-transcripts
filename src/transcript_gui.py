import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os
from pathlib import Path

# Add src to path to import generate_transcript
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir.parent))

from src.generate_transcript import generate_transcript, load_config

class TranscriptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Neuvottelija Transcript Generator")
        self.root.geometry("600x500")
        
        # Load default config if available
        self.config = {}
        try:
            self.config = load_config()
        except:
            pass

        self._init_ui()

    def _init_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="Generate Transcript", font=("Helvetica", 16, "bold")).pack(pady=(0, 20))

        # Input Grid
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        input_frame.columnconfigure(1, weight=1)

        # YouTube URL
        ttk.Label(input_frame, text="YouTube URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar(value=self.config.get("youtube_url", ""))
        ttk.Entry(input_frame, textvariable=self.url_var).grid(row=0, column=1, sticky=tk.EW, padx=5)

        # OpenAI API Key
        ttk.Label(input_frame, text="OpenAI API Key:").grid(row=1, column=0, sticky=tk.W, pady=5)
        api_key_default = self.config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY", "")
        self.api_key_var = tk.StringVar(value=api_key_default)
        ttk.Entry(input_frame, textvariable=self.api_key_var, show="*").grid(row=1, column=1, sticky=tk.EW, padx=5)

        # Language
        ttk.Label(input_frame, text="Language:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.lang_var = tk.StringVar(value=self.config.get("language", "fi"))
        ttk.Entry(input_frame, textvariable=self.lang_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5)

        # Model
        ttk.Label(input_frame, text="Model:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar(value=self.config.get("model", "whisper-1"))
        ttk.Entry(input_frame, textvariable=self.model_var, width=20).grid(row=3, column=1, sticky=tk.W, padx=5)

        # Output Basename
        ttk.Label(input_frame, text="Output Filename (no ext):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar(value=self.config.get("output_basename", "output"))
        ttk.Entry(input_frame, textvariable=self.output_var).grid(row=4, column=1, sticky=tk.EW, padx=5)

        # Generate Button
        self.generate_btn = ttk.Button(main_frame, text="Generate Transcript", command=self.start_generation)
        self.generate_btn.pack(pady=(20, 5), fill=tk.X)

        # Save Settings Button
        ttk.Button(main_frame, text="Save Settings", command=self.save_settings).pack(pady=(0, 20), fill=tk.X)

        # Log Area
        ttk.Label(main_frame, text="Log Output:").pack(anchor=tk.W)
        self.log_area = scrolledtext.ScrolledText(main_frame, height=10, state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def start_generation(self):
        url = self.url_var.get().strip()
        api_key = self.api_key_var.get().strip()
        lang = self.lang_var.get().strip()
        model = self.model_var.get().strip()
        basename = self.output_var.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        if not api_key:
            messagebox.showerror("Error", "Please enter an OpenAI API Key")
            return
        
        if "YOUR_OPENAI_API_KEY" in api_key:
            messagebox.showerror("Error", "Invalid API Key: It looks like you're using the default placeholder.\n\nPlease replace it with your actual OpenAI API Key.")
            return

        if not api_key.startswith("sk-"):
            # Warnings for common mix-ups
            if api_key.startswith("AIza"):
                messagebox.showerror("Error", "Invalid API Key: That looks like a Google/YouTube API key.\n\nThis tool requires an **OpenAI API Key** (starts with 'sk-') to perform the transcription.")
            else:
                # Soft warning, but block proceed for now as it's likely wrong
                messagebox.showerror("Error", "Invalid API Key Format.\n\nOpenAI API Keys typically start with 'sk-'.\nPlease check your key at platform.openai.com")
            return

        self.generate_btn.config(state='disabled')
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state='disabled')
        
        thread = threading.Thread(target=self.run_process, args=(url, api_key, model, lang, basename))
        thread.daemon = True
        thread.start()

    def save_settings(self):
        new_config = {
            "youtube_url": self.url_var.get().strip(),
            "output_basename": self.output_var.get().strip(),
            "model": self.model_var.get().strip(),
            "language": self.lang_var.get().strip(),
            "openai_api_key": self.api_key_var.get().strip()
        }
        
        try:
            # We need to find where config is.
            from src.generate_transcript import CONFIG_PATH
            import json
            
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(new_config, f, indent=4)
            
            messagebox.showinfo("Saved", "Settings saved to transcript_config.json")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def run_process(self, url, api_key, model, lang, basename):
        class IORedirector(object):
            def __init__(self, text_widget):
                self.text_widget = text_widget
            def write(self, str):
                self.text_widget.config(state='normal')
                self.text_widget.insert(tk.END, str)
                self.text_widget.see(tk.END)
                self.text_widget.config(state='disabled')
            def flush(self):
                pass
        
        old_stdout = sys.stdout
        sys.stdout = IORedirector(self.log_area)

        try:
            self.log("Starting process...")
            self.log(f"URL: {url}")

            sbv_path = generate_transcript(
                youtube_url=url,
                openai_api_key=api_key,
                model=model,
                language=lang,
                output_basename=basename
            )
            
            self.log("\nSUCCESS!")
            self.log(f"Transcript saved to: {sbv_path}")
            messagebox.showinfo("Success", f"Transcript generated successfully!\n\nSaved to:\n{sbv_path}")

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "insufficient_quota" in error_msg:
                 self.log(f"\nERROR: Quota Exceeded (429).")
                 messagebox.showerror("Quota Exceeded", "OpenAI API Quota Exceeded.\n\nYou have run out of credits or your billing details are invalid.\nPlease check your billing at: https://platform.openai.com/account/billing")
            else:
                self.log(f"\nERROR: {error_msg}")
                messagebox.showerror("Error", f"An error occurred:\n{error_msg}")
        finally:
            sys.stdout = old_stdout
            self.root.after(0, lambda: self.generate_btn.config(state='normal'))

if __name__ == "__main__":
    root = tk.Tk()
    app = TranscriptApp(root)
    root.mainloop()
