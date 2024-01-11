# Model Serve

Model Serve是一个易用的AI模型分布式部署工具。

我们训练好模型以后，可能需要部署给公众或第三方使用，并且需要满足一定的并发需求，除了进行AI模型的本身的加速外，一个更直接的办法是增加显卡数量、服务器数量，部署多个模型实例，完成分布式部署。从模型代码到部署代码，涉及web服务搭建、消息通信、负载均衡等问题，Model Serve把这个过程变得非常简单。

## 安装

```
git clone git@github.com:chengzl18/modelserve.git
cd modelserve
pip install -e .
```

## 使用方法

#### 代码编写

只需要将模型的初始化和推理代码填入下面的代码中，就可以进行分布式部署了。

```python
from modelserve import api, runserver_with_args


@api(name="<服务路径>")
class <任意类名>:
	def init(self, device):
		... # 模型的初始化代码
		
	def inference(self, request):
		... # 读取模型输入
		... # 模型的推理代码
		... # 返回模型输出


if __name__ == "__main__":
    runserver_with_args()
```

为了保证请求的输入输出的通用性，inference函数采取[django的输入输出](https://docs.djangoproject.com/en/5.0/ref/request-response/)形式。

#### 部署

启动controller，port是controller使用的端口号。

```bash
python <file-name>.py --controller --port <port>
```

启动worker，port是worker使用的端口号，name是与代码中一致的服务路径，device是传入init函数中的device值，controller-addr是controller访问地址（worker可以通过这个地址访问controller），worker-addr是worker的访问地址（controller可以通过这个地址访问work）。

```bash
python <file-name>.py --worker --port <port> --name <name> --device <device> --controller-addr <controller-addr> --worker-addr <worker-addr>
```

需要部署一个controller和多个worker，worker可以部署在不同的gpu或不同机器上。

#### API使用

部署完成后，`<controller-addr>/<name>`是API接口地址，可以进行调用。

#### 前端

部署为API是不需要前端的。如果你为了手动测试方便、给非技术人员试用API等其他需要，想搭建一个前端，只需要在代码同级目录编写index.html，那么浏览器访问`<controller-addr>`就是index.html的前端界面。

## 使用举例

#### 例子1

以examples中的text-to-text为例。

先下载一个text-to-text的模型google/flan-t5-base：

```bash
cd examples/text-to-text
python download.py
```

[example.py](examples/text-to-text/example.py)中填入了flan-t5-base对应的初始化代码和推理代码。在inference函数中我们从GET请求中拿出text参数作为模型的文本输入，将输出文本以json响应返回。

在本地的8888端口启动controller：

```bash
python example.py --controller --port 8888
```

在本地的8880端口，0号GPU上部署一个worker：

```bash
python example.py --worker --port 8880 --name custom --device 0 --controller-addr http://localhost:8888 --worker-addr http://localhost:8880
```

部署完成。测试api是否可用，调用api的代码在[query.py](examples/text-to-text/query.py)中：

```bash
python query.py
```

对api进行压力测试，压力测试的代码在[load_testing.py](examples/text-to-text/load_testing.py)中，压力测试会输出API系统的QPS（每秒处理请求数）：

```bash
python load_testing.py
```

下面我们部署多个worker，先关闭已有的controller和worker。为了方便一次性启动controller和全部worker，可以使用[run_all.sh](examples/text-to-text/run_all.sh)，controller和各个worker的输出会保存到对应名称的log文件中。

```bash
bash run_all.sh
```

所有worker启动后，再次进行压力测试，可以看到QPS和worker数量接近线性地提高。在一台3090机器上的测试结果为，1卡QPS=12.92，4卡QPS=47.07。

结束服务，关闭所有controller和worker，可以使用[kill_all.sh](examples/text-to-text/kill_all.sh)：

```bash
bash kill_all.sh
```

#### 例子2

以examples中的image-to-text为例。

先下载一个image-to-text的模型Salesforce/blip-image-captioning-large，以及一个demo图片：

```bash
cd examples/image-to-text
python download.py
```

[example.py](examples/image-to-text/example.py)中填入了blip-image-captioning-large对应的初始化代码和推理代码。在inference函数中我们从GET请求中读取image文件作为模型的图像输入，将输出文本以json响应返回。

同样的[query.py](examples/image-to-text/query.py)是API调用代码，[run_all.sh](examples/image-to-text/run_all.sh)是启动脚本，[test_loading.py](examples/image-to-text/query.py)是压力测试代码，[kill_all.sh](examples/image-to-text/kill_all.sh)是结束脚本，可以依次运行试用。

这个例子里我们编写了一个前端界面[index.html](examples/image-to-text/index.html)，在启动服务后，浏览器输入下面的ip地址就可以访问前端。


```bash
http://<机器公网ip地址>:<controller端口号>
```

