# do not use proxy, otherwise the controller and the worker may not be able to communicate
unset https_proxy && unset http_proxy

# run controller
nohup python example.py --controller --port 8888 > controller.log 2>&1 &
# run 8 workers on 8 gpus 
for i in {0..7}
do
    nohup python example.py --worker --port 888$i --name custom --device $i --controller-addr http://localhost:8888 --worker-addr http://localhost:888$i > worker$i.log 2>&1 &
done

# or run in seperate screens
# python example.py --controller --port 8888
# python example.py --worker --port 8880 --name custom --device 0 --controller-addr http://localhost:8888 --worker-addr http://localhost:8880
# python example.py --worker --port 8881 --name custom --device 1 --controller-addr http://localhost:8888 --worker-addr http://localhost:8881