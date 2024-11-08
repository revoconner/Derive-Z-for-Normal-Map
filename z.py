import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np
import os
import sys

class NormalMapProcessor:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Normal Map Z Reconstruction (2.0)")
        self.window.geometry("1024x800")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # code for icon handling
        try:
            # Get the base path (either script directory or _MEIPASS for PyInstaller)
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
                
            icon_path = os.path.join(base_path, "icon.ico")
            self.window.iconbitmap(icon_path)
        except Exception:
            pass  # If icon setting fails, continue without it


        self.file_paths = []
        self.processed_image = None
        
        main_frame = ctk.CTkFrame(self.window, corner_radius=10)
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        help_text = ctk.CTkLabel(main_frame, text="Selecting more than one image file will make the program behave in batch processing mode, previews will be unavailable. ",
                                wraplength=900, font=ctk.CTkFont(size=16))
        help_text.pack(pady=(10, 10), padx=20)
        
        path_frame = ctk.CTkFrame(main_frame, corner_radius=0, fg_color="transparent")
        path_frame.pack(fill=ctk.X, pady=(0, 20), padx=20)
        path_frame.grid_columnconfigure(0, weight=1)
        path_frame.grid_columnconfigure(1, weight=0)
        
        self.path_entry = ctk.CTkEntry(path_frame, height=40, placeholder_text="Select image file(s)...")
        self.path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        browse_btn = ctk.CTkButton(path_frame, text="Browse", command=self.browse_file, height=40, width=100)
        browse_btn.grid(row=0, column=1)
        
        preview_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        preview_container.pack(fill=ctk.BOTH, expand=True, padx=20, pady=10)
        
        preview_container.grid_columnconfigure(0, weight=1)
        preview_container.grid_columnconfigure(1, weight=1)
        
        self.original_preview_frame = ctk.CTkFrame(preview_container)
        self.original_preview_frame.grid(row=0, column=0, padx=10, sticky="nsew")
        
        original_title = ctk.CTkLabel(self.original_preview_frame, text="Original Image", font=ctk.CTkFont(size=16, weight="bold"))
        original_title.pack(pady=10)
        
        self.original_preview_label = ctk.CTkLabel(self.original_preview_frame, text="No image selected")
        self.original_preview_label.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
        
        self.processed_preview_frame = ctk.CTkFrame(preview_container)
        self.processed_preview_frame.grid(row=0, column=1, padx=10, sticky="nsew")
        
        processed_title = ctk.CTkLabel(self.processed_preview_frame, text="Processed Image", font=ctk.CTkFont(size=16, weight="bold"))
        processed_title.pack(pady=10)
        
        self.processed_preview_label = ctk.CTkLabel(self.processed_preview_frame, text="No processed image")
        self.processed_preview_label.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
        
        button_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_container.pack(fill=ctk.X, pady=20, padx=20)
        
        self.use_alternate = ctk.BooleanVar(value=False)
        checkbox = ctk.CTkCheckBox(button_container, text="Use alternate algorithm for linear sRGB", variable=self.use_alternate)
        checkbox.pack(pady=(0, 10))
        
        self.process_btn = ctk.CTkButton(button_container, text="Process", command=self.process_image, height=40, width=200)
        self.process_btn.pack(pady=(0, 10))
        
        self.save_btn = ctk.CTkButton(button_container, text="Save As...", command=self.save_image, height=40, width=200)
        self.save_btn.pack()
        
        self.batch_btn = ctk.CTkButton(button_container, text="Batch Process and Save As...", command=self.batch_process, height=40, width=200)
        self.batch_btn.pack()
        self.batch_btn.pack_forget()
        
        self.batch_help = ctk.CTkLabel(button_container, 
            text="In batch processing mode the images will be saved with a suffix _processed in the file format you select during save as type. Don't type anything in the filename section, doing so may result in the files being saved without an extension.",
            wraplength=900,
            font=ctk.CTkFont(size=12))
        self.batch_help.pack(pady=(20, 0))
        self.batch_help.pack_forget()

    def resize_image_for_preview(self, image, max_size=(400, 400)):
        width, height = image.size
        aspect_ratio = width / height
        
        if width > max_size[0] or height > max_size[1]:
            if aspect_ratio > 1:
                new_width = max_size[0]
                new_height = int(max_size[0] / aspect_ratio)
            else:
                new_height = max_size[1]
                new_width = int(max_size[1] * aspect_ratio)
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return image

    def update_preview(self, image, preview_label):
        if image:
            preview_image = self.resize_image_for_preview(image)
            ctk_image = ctk.CTkImage(light_image=preview_image, dark_image=preview_image, size=preview_image.size)
            preview_label.configure(image=ctk_image, text="")
        else:
            preview_label.configure(image=None)

    def browse_file(self):
        filenames = filedialog.askopenfilenames(filetypes=[("Image files", "*.png *.jpg *.jpeg *.tga *.bmp"), ("All files", "*.*")])
        self.file_paths = filenames
        
        if len(filenames) > 0:
            self.path_entry.delete(0, 'end')
            if len(filenames) == 1:
                self.path_entry.insert(0, filenames[0])
                try:
                    img = Image.open(filenames[0])
                    self.update_preview(img, self.original_preview_label)
                    self.processed_preview_label.configure(image=None, text="Click 'Process' to reconstruct normal map")
                    self.processed_image = None
                    self.process_btn.pack(pady=(0, 10))
                    self.save_btn.pack()
                    self.batch_btn.pack_forget()
                    self.process_btn.pack(pady=(0, 10))
                    self.save_btn.pack()
                    self.batch_btn.pack_forget()
                    self.batch_help.pack_forget()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")
            else:
                self.path_entry.insert(0, f"Selected {len(filenames)} files")
                self.original_preview_label.configure(image=None, text="Image preview not available for batch processing")
                self.processed_preview_label.configure(image=None, text="Image preview not available for batch processing")
                self.process_btn.pack_forget()
                self.save_btn.pack_forget()
                self.batch_btn.pack()
                self.process_btn.pack_forget()
                self.save_btn.pack_forget()
                self.batch_btn.pack()
                self.batch_help.pack(pady=(20, 0))

    def reconstruct_z(self, r, g):
        x = r * 2 - 1
        y = g * 2 - 1
        z = np.sqrt(1.0 - np.clip(x*x + y*y, 0, 1))
        norm = np.sqrt(x*x + y*y + z*z)
        x = x / norm
        y = y / norm
        z = z / norm
        return (z + 1) * 0.5

    def reconstruct_z_alternate(self, r, g):
        multiplied = np.stack([r, g], axis=-1) * 2
        subtracted = multiplied - 1
        multiplied_by_self = subtracted * subtracted
        mask_r = multiplied_by_self[..., 0]
        mask_g = multiplied_by_self[..., 1]
        one_minus_mask_r = 1 - mask_r
        final_subtract = one_minus_mask_r - mask_g
        z = np.sqrt(np.maximum(final_subtract, 0))
        return z

    def process_single_image(self, image_path):
        img = Image.open(image_path)
        img = img.convert('RGBA')
        img_array = np.array(img) / 255.0
        r = img_array[:,:,0]
        g = img_array[:,:,1]
        
        if self.use_alternate.get():
            b = self.reconstruct_z_alternate(r, g)
        else:
            b = self.reconstruct_z(r, g)
        
        new_img_array = np.zeros((*img_array.shape[:2], 3))
        new_img_array[:,:,0] = r
        new_img_array[:,:,1] = g
        new_img_array[:,:,2] = b
        new_img_array = (new_img_array * 255).astype(np.uint8)
        return Image.fromarray(new_img_array)

    def process_image(self):
        if not self.file_paths:
            messagebox.showerror("Error", "Please select an image file first.")
            return
            
        try:
            self.processed_image = self.process_single_image(self.file_paths[0])
            self.processed_preview_label.configure(text="")
            self.update_preview(self.processed_image, self.processed_preview_label)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

    def batch_process(self):
        if not self.file_paths:
            messagebox.showerror("Error", "Please select image files first.")
            return
        
        file_types = [('PNG files', '*.png'), ('JPEG files', '*.jpg'), ('TGA files', '*.tga')]
        output_format = filedialog.asksaveasfilename(
            title="Select Output Format and Directory",
            filetypes=file_types,
            initialfile="format_selection.png"
        )
        
        if not output_format:
            return
            
        output_dir = os.path.dirname(output_format)
        ext = os.path.splitext(output_format)[1].lower()
        
        progress_window = ctk.CTkToplevel(self.window)
        progress_window.title("Processing Images")
        progress_window.geometry("300x100")
        
        progress_label = ctk.CTkLabel(progress_window, text="Processing images...", font=ctk.CTkFont(size=12))
        progress_label.pack(pady=20)
        
        total_files = len(self.file_paths)
        processed_count = 0
        
        for input_path in self.file_paths:
            try:
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                output_filename = f"{base_name}_processed{ext}"
                output_path = os.path.join(output_dir, output_filename)
                
                processed_image = self.process_single_image(input_path)
                
                if ext in ['.jpg', '.jpeg']:
                    processed_image = processed_image.convert('RGB')
                    processed_image.save(output_path, "JPEG")
                elif ext == '.tga':
                    processed_image.save(output_path, "TGA")
                else:
                    processed_image.save(output_path, "PNG")
                
                processed_count += 1
                progress_label.configure(text=f"Processing images... ({processed_count}/{total_files})")
                progress_window.update()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process {input_path}:\n{str(e)}")
        
        progress_window.destroy()
        messagebox.showinfo("Success", f"Batch processing complete.\nProcessed {processed_count} out of {total_files} images.")

    def save_image(self):
        if self.processed_image is None:
            messagebox.showerror("Error", "Please process an image first.")
            return
            
        file_types = [('PNG files', '*.png'), ('JPEG files', '*.jpg'), ('TGA files', '*.tga')]
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=file_types)
        
        if save_path:
            try:
                ext = os.path.splitext(save_path)[1].lower()
                
                if ext == '.jpg' or ext == '.jpeg':
                    rgb_image = self.processed_image.convert('RGB')
                    rgb_image.save(save_path, "JPEG")
                elif ext == '.tga':
                    self.processed_image.save(save_path, "TGA")
                else:
                    self.processed_image.save(save_path, "PNG")
                    
                messagebox.showinfo("Success", f"Image saved successfully to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image:\n{str(e)}")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = NormalMapProcessor()
    app.run()
