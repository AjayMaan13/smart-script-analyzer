import openai, base64, json, os
from PIL import Image

openai.api_key = os.getenv("OPENAI_API_KEY")

def check_image_quality(image_file):
    try:
        image_file.seek(0)
        image = Image.open(image_file)
        width, height = image.size
        image_file.seek(0)
        file_size = len(image_file.getvalue())
        
        issues = []
        if width < 800 or height < 600: issues.append("Low resolution")
        if file_size < 100000: issues.append("Small file size")
        if height / width < 1.2: issues.append("Use portrait mode")
        
        scores = ["Excellent", "Good", "Fair", "Poor"]
        quality = scores[min(len(issues), 3)]
        
        return {"quality_score": quality, "issues": issues, "resolution": f"{width}x{height}", "file_size_kb": round(file_size/1024, 1)}
    except:
        return {"quality_score": "Unknown", "issues": ["Analysis failed"], "resolution": "Unknown", "file_size_kb": 0}

def analyze_receipt(image_file):
    try:
        quality_info = check_image_quality(image_file)
        image_file.seek(0)
        image_data = base64.b64encode(image_file.read()).decode()
        image_file.seek(0)
        
        prompt = f"""Analyze this receipt (Quality: {quality_info['quality_score']}).
Return JSON: {{"items": [{{"name": "item", "price": 1.99}}], "total": 15.99, "insights": ["insight1", "tip2", "observation3"], "confidence": "high/medium/low"}}"""
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
            ]}],
            max_tokens=800
        )
        
        result = json.loads(response.choices[0].message.content)
        result.update({"quality_score": quality_info['quality_score'], "quality_issues": quality_info['issues']})
        
        if quality_info['quality_score'] in ['Fair', 'Poor']:
            result['insights'].append(f"💡 Image quality is {quality_info['quality_score'].lower()}. Try clearer photo for better results.")
        
        return result
        
    except json.JSONDecodeError:
        return {"items": [{"name": "Parse error", "price": 0}], "total": 0, "insights": ["Invalid AI response", "Try again", "Check image clarity"], "quality_score": "Error", "confidence": "low"}
    except Exception as e:
        return {"items": [{"name": "Error", "price": 0}], "total": 0, "insights": [f"Error: {str(e)}", "Try clearer image", "Check lighting"], "quality_score": "Error", "confidence": "low"}