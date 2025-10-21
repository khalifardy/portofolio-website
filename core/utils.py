import markdown
from markdown.extensions import codehilite, toc
import re


def process_markdown(content):
    """Process markdown content with math support"""
    
    # Configure markdown with extensions
    md = markdown.Markdown(
        extensions=[
            'codehilite',
            'toc',
            'tables',
            'fenced_code',
            'pymdownx.arithmatex',
            'pymdownx.superfences',
            'pymdownx.highlight',
            'pymdownx.inlinehilite',
        ],
        extension_configs={
            'pymdownx.arithmatex': {
                'generic': True
            },
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': True,
            }
        }
    )
    
    # Process the content
    html_content = md.convert(content)
    
    # Apply custom post-processing
    html_content = process_custom_syntax(html_content)
    
    return html_content

def process_custom_syntax(content):
    """Process custom syntax for advanced formatting"""
    
    # Custom highlight syntax: ==highlighted text==
    content = re.sub(r'==(.*?)==', r'<mark>\1</mark>', content)
    
    # Custom underline syntax: ++underlined text++
    content = re.sub(r'\+\+(.*?)\+\+', r'<u>\1</u>', content)
    
    # Custom color syntax: {color:red}text{/color}
    content = re.sub(r'\{color:([^}]+)\}(.*?)\{/color\}', r'<span style="color: \1">\2</span>', content)
    
    # Custom size syntax: {size:large}text{/size}
    size_map = {
        'small': '0.875rem',
        'normal': '1rem', 
        'large': '1.25rem',
        'xl': '1.5rem',
        'xxl': '2rem'
    }
    
    def replace_size(match):
        size_name = match.group(1)
        text = match.group(2)
        size = size_map.get(size_name, size_name)
        return f'<span style="font-size: {size}">{text}</span>'
    
    content = re.sub(r'\{size:([^}]+)\}(.*?)\{/size\}', replace_size, content)
    
    return content

def insert_blog_images(content, blog_post):
    """Insert blog images with advanced positioning and sizing"""
    
    # Enhanced pattern for image control:
    # ![alt](image-1)
    # ![alt](image-1|small|left)
    # ![alt](image-1|medium|center|caption:"Custom caption")
    # ![alt](image-1|large|right|float)
    
    pattern = r'!\[([^\]]*)\]\(image[:-](\d+)(?:\|([^)]+))?\)'
    
    def replace_image(match):
        alt_text = match.group(1)
        image_order = int(match.group(2))
        options = match.group(3) or ""
        
        try:
            image = blog_post.images.filter(order=image_order).first()
            if not image:
                return match.group(0)
            
            # Parse options
            size_class, position_class, extra_classes, custom_caption = parse_image_options(options)
            caption = custom_caption or image.caption
            
            # Build CSS classes
            css_classes = ['blog-image']
            if size_class:
                css_classes.append(f'img-{size_class}')
            if position_class:
                css_classes.append(f'img-{position_class}')
            if extra_classes:
                css_classes.extend(extra_classes)
            
            # IMPORTANT: No leading/trailing whitespace or newlines!
            # Return HTML as single line to avoid markdown code block detection
            html = f'<figure class="{" ".join(css_classes)}">'
            html += f'<img src="{image.image.url}" alt="{image.alt_text or alt_text}" loading="lazy">'
            if caption:
                html += f'<figcaption>{caption}</figcaption>'
            html += '</figure>'
            
            return html
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return match.group(0)
    
    return re.sub(pattern, replace_image, content)
def parse_image_options(options_str):
    """Parse image options string"""
    if not options_str:
        return None, None, [], None
    
    options = [opt.strip() for opt in options_str.split('|')]
    
    size_class = None
    position_class = None
    extra_classes = []
    custom_caption = None
    
    for option in options:
        if option in ['tiny', 'small', 'medium', 'large', 'xl', 'full']:
            size_class = option
        elif option in ['left', 'center', 'right']:
            position_class = option
        elif option in ['float', 'inline', 'block']:
            extra_classes.append(option)
        elif option.startswith('caption:'):
            custom_caption = option.replace('caption:', '').strip('"\'')
        elif option.startswith('class:'):
            extra_classes.append(option.replace('class:', ''))
    
    return size_class, position_class, extra_classes, custom_caption