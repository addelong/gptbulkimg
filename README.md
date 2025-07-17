# OpenAI Bulk Image Generator

A Python script that reads a text file, splits it into paragraphs, and generates images for each paragraph using OpenAI's GPT-Image-1 API with parallel processing for improved performance.

## Features

- **Paragraph Processing**: Automatically splits text files into paragraphs (separated by empty lines)
- **Parallel Processing**: Makes concurrent API requests to speed up generation (respecting rate limits)
- **Flexible Configuration**: Configurable concurrent request limits and output directories
- **Error Handling**: Robust error handling with detailed progress reporting
- **Multiple Input Methods**: API key via command line argument or environment variable

## Prerequisites

- Python 3.7+
- OpenAI API key with access to GPT-Image-1
- Internet connection

## Installation

1. Clone or download this repository
2. Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
source venv/bin/activate  # Activate virtual environment
python main.py input.txt -k YOUR_OPENAI_API_KEY
```

### Using Environment Variable

Set your API key as an environment variable (recommended for security):

```bash
source venv/bin/activate  # Activate virtual environment
export OPENAI_API_KEY="your-api-key-here"
python main.py input.txt
```

### Advanced Usage

```bash
source venv/bin/activate  # Activate virtual environment

# Specify output directory
python main.py input.txt -o ./generated_images/

# Control concurrent requests (default: 5)
python main.py input.txt -c 3

# Specify image size
python main.py input.txt -s 1536x1024  # landscape
python main.py input.txt -s 1024x1536  # portrait
python main.py input.txt -s 1024x1024  # square

# Combine all options
python main.py input.txt -k YOUR_API_KEY -o ./images/ -c 10 -s 1536x1024
```

## Command Line Arguments

- `text_file` (required): Path to the input text file
- `-k, --api-key`: OpenAI API key (optional if set via environment variable)
- `-o, --output-dir`: Output directory for generated images (default: current directory)
- `-c, --concurrent`: Maximum number of concurrent requests (default: 5)
- `-s, --size`: Image size - auto (default), 1024x1024 (square), 1536x1024 (landscape), 1024x1536 (portrait)

## Input File Format

The input text file should contain paragraphs separated by empty lines. For example:

```
This is the first paragraph that will generate the first image.

This is the second paragraph.
It can span multiple lines.
This will generate the second image.

A third paragraph for the third image.
```

This will generate three images: `1.png`, `2.png`, and `3.png`.

## Examples

### Example 1: Simple Story Generation

Create a file called `story.txt`:
```
A majestic dragon soaring through cloudy skies above a medieval castle.

A brave knight in shining armor standing at the castle gates.

A magical forest filled with glowing mushrooms and fairy lights.
```

Run the script:
```bash
source venv/bin/activate
python main.py story.txt
```

This will generate `1.png`, `2.png`, and `3.png` in the current directory.

### Example 2: Product Descriptions

Create `products.txt`:
```
A sleek modern laptop with a metallic finish on a clean white desk.

A vintage leather messenger bag with brass buckles and rich brown color.

A minimalist coffee mug with geometric patterns in black and white.
```

Generate images in a specific folder with landscape orientation:
```bash
source venv/bin/activate
python main.py products.txt -o ./product_images/ -s 1536x1024
```

### Example 3: Creative Writing Prompts

Create `scenes.txt`:
```
A cyberpunk cityscape at night with neon lights reflecting on wet streets.

An underwater city with bioluminescent coral and swimming creatures.

A space station orbiting a distant planet with multiple moons.
```

Use environment variable and custom concurrency:
```bash
source venv/bin/activate
export OPENAI_API_KEY="your-key-here"
python main.py scenes.txt -c 2 -o ./scenes/
```

## Rate Limits and Best Practices

- **Default Concurrency**: The script defaults to 5 concurrent requests, which is conservative for most use cases
- **OpenAI Rate Limits**: GPT-Image-1 has rate limits (varies by plan). Monitor your usage to avoid hitting limits
- **Cost Awareness**: Each image generation costs money. Review your text file before running (approximately $0.01-$0.17 per image depending on quality)
- **Prompt Length**: Paragraphs are automatically truncated to 4000 characters to stay within API limits

## Output

- Images are saved as PNG files numbered sequentially (`1.png`, `2.png`, etc.)
- The script provides progress updates showing which image is being generated
- A summary is displayed at the end showing successful and failed generations

## Error Handling

The script handles various error conditions:
- Missing or invalid API key
- File not found or read errors
- API rate limit errors
- Network connectivity issues
- Invalid responses from OpenAI

Failed generations are reported but don't stop the overall process.

## Troubleshooting

### Common Issues

1. **"API key is required"**
   - Ensure you've provided the API key via `-k` argument or `OPENAI_API_KEY` environment variable

2. **"No paragraphs found"**
   - Check that your text file has content separated by empty lines
   - Ensure the file encoding is UTF-8

3. **Rate limit errors**
   - Reduce the concurrent request limit using `-c` with a lower number
   - Wait and retry if you've hit your API quota

4. **Import errors**
   - Ensure you've installed dependencies: `pip install -r requirements.txt`

### Getting Help

If you encounter issues:
1. Check the error messages - they're designed to be helpful
2. Verify your OpenAI API key has GPT-Image-1 access
3. Test with a small file first (1-2 paragraphs)

## License

This script is provided as-is for educational and practical use. Please respect OpenAI's terms of service when using their API. 