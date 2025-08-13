import os
import customtkinter as ctk
from PIL import Image
from typing import Optional, Tuple

class ProductImageHandler:
    """Utility class for handling product images"""
    
    def __init__(self, base_path: Optional[str] = None):
        """Initialize with optional base path, otherwise auto-detect"""
        if base_path:
            self.base_path = base_path
        else:
            self.base_path = self._get_base_path()
    
    def _get_base_path(self) -> str:
        """Auto-detect base path from current file location"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(current_dir)
    
    def get_product_image(self, image_path: str, size: Tuple[int, int] = (120, 80)) -> Optional[ctk.CTkImage]:
        """
        Get a CTkImage for product image or None for placeholder
        
        Args:
            image_path: Relative path to the image
            size: Tuple of (width, height) for the image
            
        Returns:
            CTkImage object or None if no image/placeholder needed
        """
        try:
            if image_path and image_path.strip():
                full_image_path = os.path.join(self.base_path, image_path)
                
                if os.path.exists(full_image_path):
                    image = Image.open(full_image_path)
                    return ctk.CTkImage(
                        light_image=image, 
                        dark_image=image, 
                        size=size
                    )
                else:
                    print(f"Image not found: {full_image_path}")
                    return None
            else:
                return None
                
        except Exception as e:
            print(f"Error loading product image {image_path}: {e}")
            return None
    
    def create_placeholder_label(self, master, size: Tuple[int, int] = (120, 80)) -> ctk.CTkLabel:
        """Create a placeholder image label with proper master"""
        return ctk.CTkLabel(
            master,
            text="", 
            fg_color="gray", 
            width=size[0], 
            height=size[1]
        )
    
    def load_image_for_display(self, image_path: str, size: Tuple[int, int] = (120, 80)) -> Optional[ctk.CTkImage]:
        """
        Load an image and return CTkImage object, or None if failed
        
        Args:
            image_path: Relative path to the image
            size: Tuple of (width, height) for the image
            
        Returns:
            CTkImage object or None if failed
        """
        try:
            if not image_path or not image_path.strip():
                return None
                
            full_image_path = os.path.join(self.base_path, image_path)
            
            if not os.path.exists(full_image_path):
                return None
                
            image = Image.open(full_image_path)
            return ctk.CTkImage(light_image=image, dark_image=image, size=size)
            
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None
    
    def validate_image_path(self, image_path: str) -> bool:
        """
        Check if an image path exists and is valid
        
        Args:
            image_path: Relative path to the image
            
        Returns:
            True if image exists and is valid, False otherwise
        """
        if not image_path or not image_path.strip():
            return False
            
        try:
            full_image_path = os.path.join(self.base_path, image_path)
            
            if not os.path.exists(full_image_path):
                return False
                
            # Try to open the image to validate it
            with Image.open(full_image_path) as img:
                img.verify()
            return True
            
        except Exception:
            return False
    
    def get_image_info(self, image_path: str) -> Optional[dict]:
        """
        Get information about an image file
        
        Args:
            image_path: Relative path to the image
            
        Returns:
            Dictionary with image info or None if failed
        """
        if not self.validate_image_path(image_path):
            return None
            
        try:
            full_image_path = os.path.join(self.base_path, image_path)
            
            with Image.open(full_image_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size_bytes': os.path.getsize(full_image_path)
                }
                
        except Exception as e:
            print(f"Error getting image info for {image_path}: {e}")
            return None