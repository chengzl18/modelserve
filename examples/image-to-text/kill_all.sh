
pid=$(pgrep -f "python example.py --controller")

if [ ! -z "$pid" ]; then
    kill $pid
    echo "kill controller: PID $pid"
else
    echo "no running controller"
fi

for i in {0..7}
do
    pid=$(pgrep -f "python example.py --worker --port 888$i")

    if [ ! -z "$pid" ]; then
        kill $pid
        echo "kill worker: PID $pid, port 888$i"
    else
        echo "no running worker 888$i"
    fi
done