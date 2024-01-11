from modelserve import api, runserver_with_args


@api(name="custom")
class Model:
    def init(self, device):
        import requests
        from PIL import Image
        from transformers import BlipProcessor, BlipForConditionalGeneration

        self.device = device
        self.processor = BlipProcessor.from_pretrained("model/blip-image-captioning-large")
        self.model = BlipForConditionalGeneration.from_pretrained("model/blip-image-captioning-large").to(self.device)

    def inference(self, request):
        from django.http import JsonResponse
        from PIL import Image
        image_file = request.FILES['image']
        image = Image.open(image_file)

        # unconditional image captioning
        inputs = self.processor(image, return_tensors="pt").to(self.device)
        out = self.model.generate(**inputs)
        text = self.processor.decode(out[0], skip_special_tokens=True)

        return JsonResponse({"text": text})


if __name__ == "__main__":
    runserver_with_args()
