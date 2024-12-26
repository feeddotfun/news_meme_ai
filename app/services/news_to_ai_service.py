import asyncio
from datetime import datetime
import base64
from typing import Dict, Optional
import aiohttp
from huggingface_hub import InferenceClient
from app.config.settings import settings
from app.models.schemas import MemeResponse

class NewsToAIService:
    def __init__(self):
        # Initialize API clients
        self.text_client = InferenceClient(
            model=settings.AI_PROMPT_MODEL,
            token=settings.AI_API_KEY
        )
        self.image_client = InferenceClient(
            model=settings.AI_IMAGE_MODEL,
            token=settings.AI_API_KEY
        )
        self.upload_api_url = settings.UPLOAD_API_URL
        self.upload_api_key = settings.UPLOAD_API_KEY

    # Generate highly creative meme name, ticker, and catchphrase based on news content
    async def _generate_meme_info(self, news: str) -> Dict[str, str]:
        prompt = f"""Based on this crypto news: "{news}"

    TASK: Create an extremely creative and witty meme coin concept.
    FORMAT YOUR RESPONSE EXACTLY LIKE THIS - INCLUDE ALL THREE LINES:
    NAME: [creative, memorable name that relates to the news]
    TICKER: [clever ticker symbol that relates to the name]
    PHRASE: [witty catchphrase with relevant emoji, avoid generic phrases]

    EXAMPLES OF GOOD RESPONSES:
    For bullish news:
    NAME: MoonBrain
    TICKER: SMART
    PHRASE: using galaxy brain moves 🧠✨

    For bearish news:
    NAME: DumpsterDive
    TICKER: OUCH
    PHRASE: catching falling knives with style 🔪💫

    For neutral news:
    NAME: CryptoYoga
    TICKER: BEND
    PHRASE: flexible like my portfolio 🧘‍♂️💰

    RULES:
    1. Be extremely creative and witty - no generic responses
    2. NAME must be clever and memorable (3-32 chars)
    3. TICKER must be witty and relevant (3-6 chars, all CAPS)
    4. PHRASE must be unique and funny - NO "to the moon" unless news is literally about space
    5. Use varied emojis - mix common and uncommon ones
    6. Match the tone of the news (bullish/bearish/neutral/funny)
    7. Create unexpected but relevant connections"""
                
        try:
            # Generate response with higher temperature for more creativity
            response = await asyncio.to_thread(
                self.text_client.text_generation,
                prompt,
                max_new_tokens=150,
                temperature=1,
                top_p=0.95,
                repetition_penalty=1.3,  # Reduce repetitive responses
                frequency_penalty=0.5 # Reduce common phrases
            )
            
            # Clean up response text
            response_text = response.strip()
            lines = [line.strip() for line in response_text.split('\n') if line.strip()]
            
            # Initialize variables
            name = ticker = phrase = None
            
            # Parse response more strictly
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.upper().startswith('NAME:'):
                    name = line.split(':', 1)[1].strip()
                elif line.upper().startswith('TICKER:'):
                    ticker = line.split(':', 1)[1].strip()
                elif line.upper().startswith('PHRASE:'):
                    phrase = line.split(':', 1)[1].strip()
            
            # Validate all components
            if not all([name, ticker, phrase]):
                print(f"Missing components in response. Got:\nname: {name}\nticker: {ticker}\nphrase: {phrase}")
                raise ValueError("Incomplete response from AI")
                
            # Additional validation
            if not (3 <= len(name) <= 32):
                raise ValueError(f"Name length invalid: {len(name)} chars")
            if not (3 <= len(ticker) <= 6):
                raise ValueError(f"Ticker length invalid: {len(ticker)} chars")
            if not ticker.isupper():
                ticker = ticker.upper()
                
            # Add default emoji if none present
            if '🚀' not in phrase and '📈' not in phrase:
                phrase = f"{phrase} 🚀"
                
            return {
                "name": name,
                "ticker": ticker,
                "phrase": phrase
            }
                
        except Exception as e:
            print(f"Error generating meme info: {str(e)}")
            print(f"Raw AI response:\n{response_text}")
            
            # Provide fallback values for common failure cases
            if not name or not (3 <= len(name) <= 32):
                name = "CryptoMeme"
            if not ticker or not (3 <= len(ticker) <= 6):
                ticker = "MEME"
            if not phrase:
                phrase = "to the moon! 🚀"
                
            return {
                "name": name,
                "ticker": ticker,
                "phrase": phrase
            }
            
    # Generate size-optimized meme image using AI model
    async def _generate_meme_image(self, news: str, name: str) -> Optional[bytes]:
        try:
            base_prompt = f"Create a funny crypto meme about {name}. Context: {news}"
            style_prompt = """
            Style guide:
            - Vibrant colors
            - Clean design
            - Crypto symbols
            - Meme style
            - Fun visual elements
            - No text overlay
            """
            
            final_prompt = f"{base_prompt}\n{style_prompt}"
            
            # Generate initial image with exact 500x500 dimensions
            response = await asyncio.to_thread(
                self.image_client.text_to_image,
                final_prompt,
                max_new_tokens=None,
                temperature=0.9,
                num_inference_steps=30,  # Reduced for faster generation
                size={
                    "width": 500,
                    "height": 500
                }
            )
            
            if response:
                import io
                from PIL import Image
                
                # Convert to PIL Image if it's not already
                if not isinstance(response, Image.Image):
                    image = Image.open(io.BytesIO(response))
                else:
                    image = response
                
                # Ensure exact 500x500 size
                if image.size != (500, 500):
                    image = image.resize((500, 500), Image.Resampling.LANCZOS)
                
                # Convert to RGB if needed
                if image.mode in ('RGBA', 'P'):
                    image = image.convert('RGB')
                
                # Save with optimization
                img_byte_arr = io.BytesIO()
                image.save(
                    img_byte_arr, 
                    format='JPEG',  # Using JPEG for smaller file size
                    optimize=True,
                    quality=85,     # Good balance of quality and size
                    progressive=True  # Progressive loading
                )
                
                # Verify final size
                final_size = len(img_byte_arr.getvalue()) / 1024  # Size in KB
                print(f"Final image size: {final_size:.2f}KB")
                
                return img_byte_arr.getvalue()
                
            return None
                
        except Exception as e:
            print(f"Image generation error: {str(e)}")
            return None

    # Upload image to cloud storage
    async def _upload_to_image(self, image_bytes: bytes) -> Optional[str]:
        try:
            if not isinstance(image_bytes, bytes):
                print("Error: image_bytes must be bytes")
                return None
                
            # Convert to base64
            b64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            params = {
                'key': self.upload_api_key
            }
            
            data = aiohttp.FormData()
            data.add_field('image', b64_image)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.upload_api_url,
                    params=params,
                    data=data,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('success'):
                            return result['data']['url']
                        print(f"Upload failed: {result.get('error', 'Unknown error')}")
                    else:
                        print(f"Upload failed with status {response.status}")
                    return None
                        
        except Exception as e:
            print(f"Upload error: {str(e)}")
            return None

    # Generate a complete meme from news
    async def generate_meme(self, news: str) -> MemeResponse:
        # Generate meme info
        meme_info = await self._generate_meme_info(news)
        
        # Generate and upload image
        image_bytes = await self._generate_meme_image(news, meme_info['name'])
        if not image_bytes:
            raise Exception("Failed to generate image")
        
        image_url = await self._upload_to_image(image_bytes)
        if not image_url:
            raise Exception("Failed to upload image")
        
        return MemeResponse(
            news=news,
            name=meme_info['name'],
            ticker=meme_info['ticker'],
            image=image_url,
            meme=f"{meme_info['name']} ({meme_info['ticker']}) {meme_info['phrase']}",
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        )

    # Process multiple news items
    async def process_news_batch(self, news_list: list[str], delay: int = 5) -> list[MemeResponse]:
        memes = []
        for news in news_list:
            meme = await self.generate_meme(news)
            memes.append(meme)
            await asyncio.sleep(delay)  # Configurable delay
        return memes