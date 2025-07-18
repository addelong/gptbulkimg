#!/usr/bin/env python3
"""
OpenAI Bulk Image Generator

A script that reads a text file, splits it into paragraphs, and generates images
for each paragraph using OpenAI's DALL-E API with parallel processing.
"""

import argparse
import asyncio
import os
import sys
import base64
from pathlib import Path
from typing import List, Tuple, Literal
from openai import AsyncOpenAI


class ImageGenerator:
    def __init__(self, api_key: str, max_concurrent: int = 5, image_size: Literal["auto", "1024x1024", "1536x1024", "1024x1536"] = "auto"):
        """
        Initialize the image generator.
        
        Args:
            api_key: OpenAI API key
            max_concurrent: Maximum number of concurrent requests (respecting rate limits)
            image_size: Size of generated images (1024x1024, 1536x1024, 1024x1536, or auto)
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.max_concurrent = max_concurrent
        self.image_size = image_size
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    def parse_text_file(self, file_path: str) -> List[str]:
        """
        Parse text file and split into paragraphs separated by empty lines.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            List of paragraph strings
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file '{file_path}': {e}")
            sys.exit(1)
            
        # Split by double newlines (empty lines) and filter out empty paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if not paragraphs:
            print("Error: No paragraphs found in the text file.")
            sys.exit(1)
            
        print(f"Found {len(paragraphs)} paragraphs to process.")
        return paragraphs
    
    async def generate_image(self, paragraph: str, index: int, output_dir: str) -> Tuple[int, bool]:
        """
        Generate an image for a single paragraph using OpenAI API and save it immediately.
        
        Args:
            paragraph: Text content to generate image from
            index: Paragraph index (for numbering)
            output_dir: Directory to save the image
            
        Returns:
            Tuple of (index, success)
        """
        async with self.semaphore:
            # Truncate paragraph if too long (gpt-image-1 has a prompt limit)
            prompt = paragraph[:4000] if len(paragraph) > 4000 else paragraph
            
            try:
                print(f"Generating image {index + 1}: {prompt[:50]}...")
                
                # Generate image using OpenAI SDK
                response = await self.client.images.generate(
                    model="gpt-image-1",
                    prompt=prompt,
                    n=1,
                    size=self.image_size,  # type: ignore
                    quality="auto"
                )
                
                # Get the base64 image data from the response
                if not response.data or len(response.data) == 0:
                    raise Exception("No image data returned from API")
                
                b64_image = response.data[0].b64_json
                if not b64_image:
                    raise Exception("No base64 image data returned from API")
                
                # Decode the base64 image data
                image_data = base64.b64decode(b64_image)
                
                # Save image immediately
                filename = f"{index + 1}.png"
                filepath = Path(output_dir) / filename
                
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                print(f"Saved: {filepath}")
                return index, True
                    
            except Exception as e:
                print(f"Error generating image {index + 1}: {e}")
                return index, False
    
    async def process_paragraphs(self, paragraphs: List[str], output_dir: str = "."):
        """
        Process all paragraphs and generate images in parallel.
        
        Args:
            paragraphs: List of paragraph strings
            output_dir: Directory to save images
        """
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(exist_ok=True)
        
        # Create tasks for all paragraphs
        tasks = [
            self.generate_image(paragraph, i, output_dir)
            for i, paragraph in enumerate(paragraphs)
        ]
        
        # Process all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count results
        successful = 0
        failed = 0
        
        for result in results:
            if isinstance(result, BaseException):
                print(f"Task failed with exception: {result}")
                failed += 1
                continue
            
            index, success = result
            
            if success:
                successful += 1
            else:
                failed += 1
        
        print(f"\nCompleted! {successful} images generated successfully, {failed} failed.")


def main():
    """Main function to parse arguments and run the image generator."""
    parser = argparse.ArgumentParser(
        description="Generate images from text paragraphs using OpenAI's GPT-Image-1 API"
    )
    parser.add_argument(
        "text_file",
        help="Path to the text file containing paragraphs separated by empty lines"
    )
    parser.add_argument(
        "-k", "--api-key",
        help="OpenAI API key (can also be set via OPENAI_API_KEY environment variable)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Output directory for generated images (default: current directory)"
    )
    parser.add_argument(
        "-c", "--concurrent",
        type=int,
        default=5,
        help="Maximum number of concurrent requests (default: 5)"
    )
    parser.add_argument(
        "-s", "--size",
        choices=["auto", "1024x1024", "1536x1024", "1024x1536"],
        default="auto",
        help="Size of generated images: auto (default), 1024x1024 (square), 1536x1024 (landscape), 1024x1536 (portrait)"
    )
    
    args = parser.parse_args()
    
    # Get API key from argument or environment variable
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key is required. Provide it via -k argument or OPENAI_API_KEY environment variable.")
        sys.exit(1)
    
    # Create generator and run
    generator = ImageGenerator(api_key, max_concurrent=args.concurrent, image_size=args.size)
    paragraphs = generator.parse_text_file(args.text_file)
    
    # Run the async processing
    asyncio.run(generator.process_paragraphs(paragraphs, args.output_dir))


if __name__ == "__main__":
    main() 