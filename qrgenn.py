#!/usr/bin/env python3
"""
QR Code  Generator CLI Application
A command-line tool to generate QR codes from text input with customization options.
Compatible with standard qrcode library.
"""
print("hiii")       

import argparse
import sys
import os
from pathlib import Path
import qrcode
from PIL import Image, ImageDraw, ImageFont
import colorama
from colorama import Fore, Style, Back
import qrcode.image.svg

# Initialize colorama for cross-platform colored output
colorama.init()

class QRGenerator:
    def __init__(self):
        self.supported_formats = ['PNG', 'JPEG', 'BMP', 'TIFF', 'SVG']
    
    def generate_qr(self, text, **kwargs):
        """Generate QR code with specified parameters"""
        try:
            format_type = kwargs.get('format_type', 'PNG').upper()
            # QR Code configuration
            qr = qrcode.QRCode(
                version=kwargs.get('version', 1),
                error_correction=self.get_error_correction(kwargs.get('error_correction', 'M')),
                box_size=kwargs.get('box_size', 10),
                border=kwargs.get('border', 4),
            )
            qr.add_data(text)
            qr.make(fit=True)
            if format_type == 'SVG':
                img = qr.make_image(image_factory=qrcode.image.svg.SvgImage)
            else:
                img = qr.make_image(
                    fill_color=kwargs.get('fill_color', 'black'),
                    back_color=kwargs.get('back_color', 'white')
                )
            return img, None
        except Exception as e:
            return None, str(e)
    
    def get_error_correction(self, level):
        """Get error correction level"""
        levels = {
            'L': qrcode.constants.ERROR_CORRECT_L,  # ~7%
            'M': qrcode.constants.ERROR_CORRECT_M,  # ~15%
            'Q': qrcode.constants.ERROR_CORRECT_Q,  # ~25%
            'H': qrcode.constants.ERROR_CORRECT_H   # ~30%
        }
        return levels.get(level.upper(), qrcode.constants.ERROR_CORRECT_M)
    
    def add_logo(self, qr_img, logo_path, logo_size_ratio=0.2):
        """Add logo to the center of QR code"""
        try:
            if not os.path.exists(logo_path):
                return qr_img, f"Logo file not found: {logo_path}"
            
            logo = Image.open(logo_path)
            
            # Convert QR image to RGB if it's not already
            if qr_img.mode != 'RGB':
                qr_img = qr_img.convert('RGB')
            
            # Calculate logo size
            qr_width, qr_height = qr_img.size
            logo_size = int(min(qr_width, qr_height) * logo_size_ratio)
            
            # Resize logo maintaining aspect ratio
            logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Create a white background for the logo
            logo_bg_size = logo_size + 20
            logo_bg = Image.new('RGB', (logo_bg_size, logo_bg_size), 'white')
            
            # Center the logo on the white background
            logo_pos = ((logo_bg_size - logo.size[0]) // 2, (logo_bg_size - logo.size[1]) // 2)
            
            # Handle logo transparency
            if logo.mode == 'RGBA':
                logo_bg.paste(logo, logo_pos, logo)
            else:
                logo_bg.paste(logo, logo_pos)
            
            # Calculate position to center the logo on QR code
            pos = ((qr_width - logo_bg_size) // 2, (qr_height - logo_bg_size) // 2)
            
            # Paste logo onto QR code
            qr_img.paste(logo_bg, pos)
            return qr_img, None
            
        except Exception as e:
            return qr_img, f"Could not add logo: {e}"
    
    def create_rounded_qr(self, qr_img, corner_radius=10):
        """Create rounded corners for QR code"""
        try:
            # Convert to RGB if needed
            if qr_img.mode != 'RGB':
                qr_img = qr_img.convert('RGB')
            
            # Create a mask for rounded corners
            mask = Image.new('L', qr_img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([0, 0, qr_img.size[0], qr_img.size[1]], 
                                 corner_radius, fill=255)
            
            # Apply the mask
            output = Image.new('RGBA', qr_img.size, (0, 0, 0, 0))
            output.paste(qr_img, (0, 0))
            output.putalpha(mask)
            
            return output, None
            
        except Exception as e:
            return qr_img, f"Could not create rounded corners: {e}"
    
    def save_qr(self, img, output_path, format_type='PNG'):
        """Save QR code image"""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if format_type.upper() == 'SVG':
                # Save SVG as text (decode bytes to str)
                svg_data = img.to_string()
                if isinstance(svg_data, bytes):
                    svg_data = svg_data.decode('utf-8')
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(svg_data)
                return True, str(output_path)
            if format_type.upper() == 'JPEG' and img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, 'white')
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            img.save(output_path, format_type.upper())
            return True, str(output_path)
        except Exception as e:
            return False, str(e)

def print_banner():
    """Print application banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════╗
║           QR Code Generator          ║
║        Command Line Interface       ║
╚══════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def print_success(message):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    """Print error message"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    """Print info message"""
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")

def print_warning(message):
    """Print warning message"""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")

def validate_color(color):
    """Validate color input"""
    try:
        # Try to create a PIL color - this validates the color
        Image.new('RGB', (1, 1), color)
        return True
    except:
        # Try common color names and hex formats
        valid_colors = ['black', 'white', 'red', 'green', 'blue', 'yellow', 
                       'cyan', 'magenta', 'orange', 'purple', 'pink', 'brown', 'gray']
        if color.lower() in valid_colors:
            return True
        # Check hex format
        if color.startswith('#') and len(color) in [4, 7]:
            try:
                int(color[1:], 16)
                return True
            except:
                pass
        return False

def get_text_input():
    """Get text input from user with validation"""
    while True:
        text = input(f"{Fore.YELLOW}Enter text to encode: {Style.RESET_ALL}").strip()
        if text:
            return text
        print_error("Text cannot be empty!")

def get_filename_input(default="qrcode.png"):
    """Get output filename with validation"""
    while True:
        filename = input(f"{Fore.YELLOW}Output filename [{default}]: {Style.RESET_ALL}").strip()
        if not filename:
            return default
        
        # Validate filename
        try:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            return filename
        except:
            print_error("Invalid filename or path!")

def interactive_mode():
    """Interactive mode for QR code generation"""
    print_banner()
    print_info("Interactive Mode - Follow the prompts to generate your QR code")
    print()
    
    # Get text input
    text = get_text_input()
    
    # Get output filename
    output = get_filename_input()
    
    # Get customization options
    print(f"\n{Fore.CYAN}Customization Options (press Enter for defaults):{Style.RESET_ALL}")
    
    # Box size
    while True:
        size_input = input(f"{Fore.YELLOW}Box size (1-50) [10]: {Style.RESET_ALL}").strip()
        if not size_input:
            size = 10
            break
        try:
            size = int(size_input)
            if 1 <= size <= 50:
                break
            else:
                print_error("Box size must be between 1 and 50")
        except ValueError:
            print_error("Please enter a valid number")
    
    # Border size
    while True:
        border_input = input(f"{Fore.YELLOW}Border size (0-20) [4]: {Style.RESET_ALL}").strip()
        if not border_input:
            border = 4
            break
        try:
            border = int(border_input)
            if 0 <= border <= 20:
                break
            else:
                print_error("Border size must be between 0 and 20")
        except ValueError:
            print_error("Please enter a valid number")
    
    # Colors with validation
    while True:
        fill_color = input(f"{Fore.YELLOW}Fill color [black]: {Style.RESET_ALL}").strip()
        if not fill_color:
            fill_color = 'black'
            break
        if validate_color(fill_color):
            break
        print_error("Invalid color! Use color names (red, blue, etc.) or hex (#FF0000)")
    
    while True:
        back_color = input(f"{Fore.YELLOW}Background color [white]: {Style.RESET_ALL}").strip()
        if not back_color:
            back_color = 'white'
            break
        if validate_color(back_color):
            break
        print_error("Invalid color! Use color names (red, blue, etc.) or hex (#FF0000)")
    
    # Error correction
    while True:
        error_correction = input(f"{Fore.YELLOW}Error correction (L/M/Q/H) [M]: {Style.RESET_ALL}").strip().upper()
        if not error_correction:
            error_correction = 'M'
            break
        if error_correction in ['L', 'M', 'Q', 'H']:
            break
        print_error("Please enter L, M, Q, or H")
    
    # Logo option
    logo_path = None
    add_logo = input(f"{Fore.YELLOW}Add logo? (y/n) [n]: {Style.RESET_ALL}").strip().lower()
    if add_logo in ['y', 'yes']:
        while True:
            logo_input = input(f"{Fore.YELLOW}Logo file path: {Style.RESET_ALL}").strip()
            if os.path.exists(logo_input):
                logo_path = logo_input
                break
            elif not logo_input:
                print_info("Skipping logo...")
                break
            else:
                print_error("File not found! Please enter a valid path.")
    
    # Rounded corners
    rounded = input(f"{Fore.YELLOW}Add rounded corners? (y/n) [n]: {Style.RESET_ALL}").strip().lower()
    add_rounded = rounded in ['y', 'yes']
    
    # Output format
    while True:
        format_input = input(f"{Fore.YELLOW}Output format (PNG/JPEG/BMP/TIFF/SVG) [PNG]: {Style.RESET_ALL}").strip().upper()
        if not format_input:
            format_type = 'PNG'
            break
        if format_input in ['PNG', 'JPEG', 'BMP', 'TIFF', 'SVG']:
            format_type = format_input
            break
        print_error("Invalid format! Choose from PNG, JPEG, BMP, TIFF, SVG.")
    
    # Generate QR code
    generator = QRGenerator()
    
    try:
        print_info("Generating QR code...")
        img, error = generator.generate_qr(
            text,
            box_size=size,
            border=border,
            fill_color=fill_color,
            back_color=back_color,
            error_correction=error_correction,
            format_type=format_type
        )
        
        if error:
            print_error(f"Error generating QR code: {error}")
            return
        
        # Add logo if specified (not supported for SVG)
        if logo_path and format_type != 'SVG':
            print_info("Adding logo...")
            img, logo_error = generator.add_logo(img, logo_path)
            if logo_error:
                print_warning(logo_error)
        elif logo_path and format_type == 'SVG':
            print_warning("Logos are not supported for SVG output. Skipping logo.")
        
        # Add rounded corners if requested (not supported for SVG)
        if add_rounded and format_type != 'SVG':
            print_info("Adding rounded corners...")
            img, round_error = generator.create_rounded_qr(img)
            if round_error:
                print_warning(round_error)
        elif add_rounded and format_type == 'SVG':
            print_warning("Rounded corners are not supported for SVG output. Skipping.")
        
        # Save QR code
        success, result = generator.save_qr(img, output, format_type)
        
        if success:
            print_success(f"QR code saved as: {result}")
            print_info(f"QR code contains: {text}")
            if format_type != 'SVG':
                print_info(f"Size: {img.size[0]}x{img.size[1]} pixels")
            
            # Display QR info
            error_levels = {'L': '~7%', 'M': '~15%', 'Q': '~25%', 'H': '~30%'}
            print_info(f"Error correction: {error_correction} ({error_levels[error_correction]})")
        else:
            print_error(f"Failed to save QR code: {result}")
            
    except Exception as e:
        print_error(f"Unexpected error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate QR codes from text input with customization options",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Hello World"
  %(prog)s "https://example.com" -o website.png -s 15 -b 2
  %(prog)s "Contact: +1234567890" -f blue -bg yellow -e H
  %(prog)s --interactive
  %(prog)s "My Text" --logo logo.png --rounded
        """
    )
    
    # Main arguments
    parser.add_argument('text', nargs='?', help='Text to encode in QR code')
    parser.add_argument('-o', '--output', default='qrcode.png', 
                       help='Output filename (default: qrcode.png)')
    
    # QR Code parameters
    parser.add_argument('-s', '--size', type=int, default=10, 
                       help='Box size for each module (default: 10)')
    parser.add_argument('-b', '--border', type=int, default=4, 
                       help='Border size in modules (default: 4)')
    parser.add_argument('-e', '--error-correction', choices=['L', 'M', 'Q', 'H'], 
                       default='M', help='Error correction level (default: M)')
    parser.add_argument('-v', '--version', type=int, choices=range(1, 41), 
                       help='QR code version (1-40, auto if not specified)')
    
    # Styling options
    parser.add_argument('-f', '--fill-color', default='black', 
                       help='Fill color for QR modules (default: black)')
    parser.add_argument('-bg', '--back-color', default='white', 
                       help='Background color (default: white)')
    
    # Additional features
    parser.add_argument('--logo', help='Path to logo image to embed in QR code')
    parser.add_argument('--logo-size', type=float, default=0.2, 
                       help='Logo size ratio (0.1-0.4, default: 0.2)')
    parser.add_argument('--rounded', action='store_true',
                       help='Add rounded corners to QR code')
    parser.add_argument('--format', choices=['PNG', 'JPEG', 'BMP', 'TIFF', 'SVG'], default='PNG',
                       help='Output format (default: PNG, supports: PNG, JPEG, BMP, TIFF, SVG)')
    
    # Modes
    parser.add_argument('-i', '--interactive', action='store_true', 
                       help='Run in interactive mode')
    parser.add_argument('--batch', help='Batch process from file (one text per line)')
    parser.add_argument('--quiet', action='store_true', help='Suppress output messages')
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    # Batch mode
    if args.batch:
        if not os.path.exists(args.batch):
            print_error(f"Batch file not found: {args.batch}")
            sys.exit(1)
            
        try:
            with open(args.batch, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
            
            if not lines:
                print_error("Batch file is empty or contains no valid lines")
                sys.exit(1)
            
            generator = QRGenerator()
            success_count = 0
            
            for i, text in enumerate(lines, 1):
                output_name = f"{Path(args.output).stem}_{i}{Path(args.output).suffix}"
                
                img, error = generator.generate_qr(
                    text,
                    box_size=args.size,
                    border=args.border,
                    fill_color=args.fill_color,
                    back_color=args.back_color,
                    error_correction=args.error_correction,
                    version=args.version,
                    format_type=args.format
                )
                
                if error:
                    if not args.quiet:
                        print_error(f"Failed to generate QR for line {i}: {error}")
                    continue
                
                if args.logo:
                    img, logo_error = generator.add_logo(img, args.logo, args.logo_size)
                    if logo_error and not args.quiet:
                        print_warning(f"Logo warning for {output_name}: {logo_error}")
                
                if args.rounded:
                    img, round_error = generator.create_rounded_qr(img)
                    if round_error and not args.quiet:
                        print_warning(f"Rounded corners warning for {output_name}: {round_error}")
                
                success, result = generator.save_qr(img, output_name, args.format)
                
                if success:
                    success_count += 1
                    if not args.quiet:
                        print_success(f"Generated {output_name} for: {text[:50]}{'...' if len(text) > 50 else ''}")
                else:
                    if not args.quiet:
                        print_error(f"Failed to save {output_name}: {result}")
            
            if not args.quiet:
                print_success(f"Batch processing complete! Generated {success_count}/{len(lines)} QR codes.")
                
        except Exception as e:
            print_error(f"Batch processing error: {e}")
            sys.exit(1)
        return
    
    # Standard mode - require text input
    if not args.text:
        parser.print_help()
        print(f"\n{Fore.YELLOW}💡 Tip: Use --interactive for guided QR code generation{Style.RESET_ALL}")
        sys.exit(1)
    
    # Validate parameters
    if args.size < 1 or args.size > 50:
        print_error("Box size must be between 1 and 50")
        sys.exit(1)
    
    if args.border < 0 or args.border > 20:
        print_error("Border size must be between 0 and 20")
        sys.exit(1)
    
    if args.logo_size < 0.1 or args.logo_size > 0.4:
        print_error("Logo size ratio must be between 0.1 and 0.4")
        sys.exit(1)
    
    # Validate colors
    if not validate_color(args.fill_color):
        print_error(f"Invalid fill color: {args.fill_color}")
        print_info("Use color names (red, blue, etc.) or hex codes (#FF0000)")
        sys.exit(1)
    
    if not validate_color(args.back_color):
        print_error(f"Invalid background color: {args.back_color}")
        print_info("Use color names (red, blue, etc.) or hex codes (#FF0000)")
        sys.exit(1)
    
    # Generate QR code
    generator = QRGenerator()
    
    try:
        if not args.quiet:
            print_info("Generating QR code...")
        
        img, error = generator.generate_qr(
            args.text,
            box_size=args.size,
            border=args.border,
            fill_color=args.fill_color,
            back_color=args.back_color,
            error_correction=args.error_correction,
            version=args.version,
            format_type=args.format
        )
        
        if error:
            print_error(f"Error generating QR code: {error}")
            sys.exit(1)
        
        # Add logo if specified (not supported for SVG)
        if args.logo and args.format != 'SVG':
            if not args.quiet:
                print_info("Adding logo...")
            img, logo_error = generator.add_logo(img, args.logo, args.logo_size)
            if logo_error and not args.quiet:
                print_warning(logo_error)
        
        # Add rounded corners if requested (not supported for SVG)
        if args.rounded and args.format != 'SVG':
            if not args.quiet:
                print_info("Adding rounded corners...")
            img, round_error = generator.create_rounded_qr(img)
            if round_error and not args.quiet:
                print_warning(round_error)
        
        # Save QR code
        success, result = generator.save_qr(img, args.output, args.format)
        
        if success:
            if not args.quiet:
                print_success(f"QR code saved as: {result}")
                print_info(f"Text encoded: {args.text}")
                if args.format != 'SVG':
                    print_info(f"Image size: {img.size[0]}x{img.size[1]} pixels")
                
                # Display additional info
                error_levels = {'L': '~7%', 'M': '~15%', 'Q': '~25%', 'H': '~30%'}
                print_info(f"Error correction: {args.error_correction} ({error_levels[args.error_correction]})")
        else:
            print_error(f"Failed to save QR code: {result}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print_error("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
