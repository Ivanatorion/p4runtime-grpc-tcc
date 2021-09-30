cd ../../../
export LD_LIBRARY_PATH=./platform_api/lib/hwtestlib/
export PYTHONPATH=.
timeout 20 python examples/attacks/CDF/TriggerApp/admin_app.py
