import gradio as gr
import torch

from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large", torch_dtype=torch.float16).to("cuda")

hf_token = os.environ.get('HF_TOKEN')
from gradio_client import Client
client = Client("https://fffiloni-test-llama-api.hf.space/", hf_token=hf_token)

def infer(image_input):
    #img_url = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/demo.jpg' 
    raw_image = Image.open(image_input).convert('RGB')

    # unconditional image captioning
    inputs = processor(raw_image, return_tensors="pt").to("cuda", torch.float16)

    out = model.generate(**inputs)

    caption = processor.decode(out[0], skip_special_tokens=True)
    print(caption)

    llama_q = f"""
    I'll give you a simple image caption, from i want you to provide a story that would fit well with the image.
    
    Here's the music description :
    
    {caption}
    
    """
    
    result = client.predict(
    				llama_q,	# str in 'Message' Textbox component
    				api_name="/predict"
    )

    
    
    
    print(f"Llama2 result: {result}")

    return caption, result

css="""
#col-container {max-width: 910px; margin-left: auto; margin-right: auto;}
a {text-decoration-line: underline; font-weight: 600;}
"""

with gr.Blocks(css=css) as demo:
    with gr.Column(elem_id="col-container"):
        gr.Markdown(
            """
            # Image to Story
            Upload an image, get a story ! 
            <br/>
            <br/>
            [![Duplicate this Space](https://huggingface.co/datasets/huggingface/badges/raw/main/duplicate-this-space-sm.svg)](https://huggingface.co/spaces/fffiloni/SplitTrack2MusicGen?duplicate=true) for longer audio, more control and no queue.</p>
            """
        )
        image_in = gr.Image(label="Image input", type="filepath")
        submit_btn = gr.Button('Sumbit')
        caption = gr.Textbox(label="Generated Caption")
        story = gr.Textbox(label="generated Story")
    submit_btn.click(fn=infer, inputs=[image_in], outputs=[caption, story])

demo.queue().launch()