unset https_proxy && unset http_proxy
nohup python example.py --controller --port 8888 > controller.log 2>&1 &
for i in {0..7}
do
    nohup python example.py --worker --port 888$i --name custom --device cuda:$i --controller-addr http://localhost:8888 --worker-addr http://localhost:888$i > worker$i.log 2>&1 &
done
