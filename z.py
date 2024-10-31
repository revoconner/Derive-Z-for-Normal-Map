import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np
import os

class NormalMapProcessor:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Normal Map Z Reconstruction")
        self.window.geometry("1024x800")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # File path variable
        self.file_path = ctk.StringVar()
        self.processed_image = None
        
        # Create main frame
        main_frame = ctk.CTkFrame(self.window, corner_radius=10)
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        # Create file path entry
        path_frame = ctk.CTkFrame(main_frame, corner_radius=0, fg_color="transparent")
        path_frame.pack(fill=ctk.X, pady=(0, 20), padx=20)
        path_frame.grid_columnconfigure(0, weight=1)
        path_frame.grid_columnconfigure(1, weight=0)
        
        self.path_entry = ctk.CTkEntry(path_frame, textvariable=self.file_path, 
                                     height=40, placeholder_text="Select an image file...")
        self.path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        browse_btn = ctk.CTkButton(path_frame, text="Browse", command=self.browse_file, 
                                 height=40, width=100)
        browse_btn.grid(row=0, column=1)
        
        # Create preview frames
        preview_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        preview_container.pack(fill=ctk.BOTH, expand=True, padx=20, pady=10)
        
        # Configure preview container columns
        preview_container.grid_columnconfigure(0, weight=1)
        preview_container.grid_columnconfigure(1, weight=1)
        
        # Original image preview
        self.original_preview_frame = ctk.CTkFrame(preview_container)
        self.original_preview_frame.grid(row=0, column=0, padx=10, sticky="nsew")
        
        original_title = ctk.CTkLabel(self.original_preview_frame, text="Original Image",
                                    font=ctk.CTkFont(size=16, weight="bold"))
        original_title.pack(pady=10)
        
        self.original_preview_label = ctk.CTkLabel(self.original_preview_frame, text="No image selected")
        self.original_preview_label.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
        
        # Processed image preview
        self.processed_preview_frame = ctk.CTkFrame(preview_container)
        self.processed_preview_frame.grid(row=0, column=1, padx=10, sticky="nsew")
        
        processed_title = ctk.CTkLabel(self.processed_preview_frame, text="Processed Image",
                                     font=ctk.CTkFont(size=16, weight="bold"))
        processed_title.pack(pady=10)
        
        self.processed_preview_label = ctk.CTkLabel(self.processed_preview_frame, text="No processed image")
        self.processed_preview_label.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
        
        # Button container
        button_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_container.pack(fill=ctk.X, pady=20, padx=20)
        
        # Create process button
        process_btn = ctk.CTkButton(button_container, text="Process", 
                                  command=self.process_image, 
                                  height=40, width=200)
        process_btn.pack(pady=(0, 10))
        
        # Create save button
        save_btn = ctk.CTkButton(button_container, text="Save As...", 
                                command=self.save_image,
                                height=40, width=200)
        save_btn.pack()

    def resize_image_for_preview(self, image, max_size=(400, 400)):
        # Calculate aspect ratio
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
            # Resize the image
            preview_image = self.resize_image_for_preview(image)
            # Convert to CTkImage
            ctk_image = ctk.CTkImage(light_image=preview_image, 
                                   dark_image=preview_image,
                                   size=preview_image.size)
            preview_label.configure(image=ctk_image, text="")  # Clear text when showing image
        else:
            preview_label.configure(image=None)  # Clear image

    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.tga *.bmp"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.file_path.set(filename)
            try:
                # Load and show preview
                img = Image.open(filename)
                self.update_preview(img, self.original_preview_label)
                # Clear processed preview when new image is loaded (error before keep in mind)
                self.processed_preview_label.configure(image=None, text="Click 'Process' to reconstruct normal map")
                self.processed_image = None
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")

    def reconstruct_z(self, r, g):
        # Convert to range -1 to 1
        x = r * 2 - 1
        y = g * 2 - 1
        
        # Z calculation
        z = np.sqrt(1.0 - np.clip(x*x + y*y, 0, 1))
        
        # Normalize the vector
        norm = np.sqrt(x*x + y*y + z*z)
        x = x / norm
        y = y / norm
        z = z / norm
        
        # Convert back to 0 to 1 range
        return (z + 1) * 0.5

    def process_image(self):
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select an image file first.")
            return
            
        try:
            # Load image
            img = Image.open(self.file_path.get())
            img = img.convert('RGBA')  # Convert to RGBA to ensure consistent processing (imp!!!)
            
            # Convert to numpy array and normalize to 0-1 range
            img_array = np.array(img) / 255.0
            
            # Get R and G channels
            r = img_array[:,:,0]
            g = img_array[:,:,1]
            
            # Reconstruct Z channel
            b = self.reconstruct_z(r, g)
            
            # Create new image array (imp!!!)
            new_img_array = np.zeros((*img_array.shape[:2], 3))
            new_img_array[:,:,0] = r  # Original R
            new_img_array[:,:,1] = g  # Original G
            new_img_array[:,:,2] = b  # Reconstructed B
            
            # Convert back to 0-255 range
            new_img_array = (new_img_array * 255).astype(np.uint8)
            
            # Create new image
            self.processed_image = Image.fromarray(new_img_array)
            
            # Update preview with empty text
            self.processed_preview_label.configure(text="")  # Clear text before showing image (revised)
            self.update_preview(self.processed_image, self.processed_preview_label)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

    def save_image(self):
        if self.processed_image is None:
            messagebox.showerror("Error", "Please process an image first.")
            return
            
        file_types = [
            ('PNG files', '*.png'),
            ('JPEG files', '*.jpg'),
            ('TGA files', '*.tga')
        ]
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=file_types
        )
        
        if save_path:
            try:
                # Get file extension
                ext = os.path.splitext(save_path)[1].lower()
                
              
                if ext == '.jpg' or ext == '.jpeg':
                    # Convert to RGB for JPEG
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