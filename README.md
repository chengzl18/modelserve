# Model Serve

[中文文档](README-zh.md)

Model Serve is an easy-to-use tool for distributed deployment of AI models.

After training our models, we may need to deploy them for public or third-party use, meeting certain concurrency demands. Besides accelerating the AI model itself, a more direct method is to increase the number of GPUs and servers, deploying multiple model instances. From model code to deployment code, this involves setting up web services, message communication, load balancing, etc. Model Serve simplifies this process.

## Installation

```
git clone git@github.com:chengzl18/modelserve.git
cd modelserve
pip install -e .
```

## Usage

#### Code Writing

Just fill in the model's initialization and inference code in the following script for distributed deployment.

```python
from modelserve import api, runserver_with_args


@api(name="<path>")
class <AnyClassName>:
	def init(self, device):
		... # Model initialization code
		
	def inference(self, request):
		... # Read model input
		... # Model inference code
		... # Return model output


if __name__ == "__main__":
    runserver_with_args()
```

To ensure the generality of request inputs and outputs, the inference function adopts the form of [Django's request-response](https://docs.djangoproject.com/en/5.0/ref/request-response/).

#### Deployment

Start the controller, where port is the port number used by the controller.

```bash
python <file-name>.py --controller --port <port>
```

Start a worker, where port is the worker's port number, name is the service path consistent with the code, device is the device value passed to the init function, controller-addr is the controller's access address (worker accesses the controller via this address), worker-addr is the worker's access address (controller accesses the worker via this address).

```bash
python <file-name>.py --worker --port <port> --name <name> --device <device> --controller-addr <controller-addr> --worker-addr <worker-addr>
```

You need to deploy one controller and multiple workers, with workers deployable on different GPUs or machines.

#### API Usage

Once deployed, `<controller-addr>/<name>` is the API interface address, available for calls.

#### Web Frontend

Deploying as an API doesn't require a frontend. If you want to build a frontend for manual testing convenience, for non-technical personnel to try the API, etc., just write an index.html in the same directory as the code. Then the browser accessing `<controller-addr>` will display the index.html frontend interface.

## Examples

#### Example 1

Take the text-to-text example in examples.

First, download a text-to-text model google/flan-t5-base:

```bash
cd examples/text-to-text
python download.py
```

[examples.py](example/text-to-text/example.py) contains the corresponding initialization and inference code for flan-t5-base. In the inference function, we extract the text parameter from the GET request as the model's text input and return the output text in a JSON response.

Start a controller on local port 8888:

```bash
python example.py --controller --port 8888
```

Deploy a worker on local port 8880, on GPU 0:

```bash
python example.py --worker --port 8880 --name custom --device 0 --controller-addr http://localhost:8888 --worker-addr http://localhost:8880
```

Once deployed, test if the API is functional with code in [query.py](examples/text-to-text/query.py):

```bash
python query.py
```

Conduct a load test of the API with [load_testing.py](examples/text-to-text/load_testing.py), which outputs the API system's QPS (queries per second):

```bash
python load_testing.py
```

Next, deploy multiple workers. First, shut down the existing controller and worker. To conveniently start the controller and all workers at once, use [run_all.sh](examples/text-to-text/run_all.sh); the output of the controller and each worker will be saved in corresponding log files.

```bash
bash run_all.sh
```

After starting all workers, conduct the stress test again to see the QPS nearly linearly increasing with the number of workers. Test results on a 3090 machine show: 1 GPU QPS=12.92, 4 GPUs QPS=47.07.

To end the service and shut down all controllers and workers, use [kill_all.sh](examples/text-to-text/kill_all.sh):

```bash
bash kill_all.sh
```

#### Example 2

Take the image-to-text example in examples.

First, download an image-to-text model Salesforce/blip-image-captioning-large, along with a demo image:

```bash
cd examples/image-to-text
python download.py
```

[examples.py](example/image-to-text/example.py) includes the initialization and inference code corresponding to the Salesforce/blip-image-captioning-large model. In the inference function, we read the image file from the GET request as the model's image input and return the output text in a JSON response.

The same [query.py](examples/image-to-text/query.py) is for API calling, [run_all.sh](examples/image-to-text/run_all.sh) for starting the service, [test_loading.py](examples/image-to-text/query.py) for load testing, and [kill_all.sh](examples/image-to-text/kill_all.sh) for ending the service; these can be run sequentially for trial use.

In this example, we have written a frontend interface [index.html](examples/image-to-text/index.html). After starting the service, you can access the frontend by entering the following IP address in a browser.


```bash
http://<machine public IP address>:<controller port>
```

