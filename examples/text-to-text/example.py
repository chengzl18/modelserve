from modelserve import api, runserver_with_args


@api(name="custom")
class Model:
    def init(self, device):
        import os
        os.environ['CUDA_VISIBLE_DEVICES'] = device
        from transformers import T5Tokenizer, T5ForConditionalGeneration
        self.tokenizer = T5Tokenizer.from_pretrained("model/flan-t5-base")
        self.model = T5ForConditionalGeneration.from_pretrained("model/flan-t5-base", device_map="auto")

    def inference(self, request):
        from django.http import JsonResponse
        input_text = request.GET['text']
        input_ids = self.tokenizer(input_text, return_tensors="pt").input_ids.to("cuda")

        outputs = self.model.generate(input_ids)
        text = self.tokenizer.decode(outputs[0])
        return JsonResponse({"text": text})


if __name__ == "__main__":
    runserver_with_args()
