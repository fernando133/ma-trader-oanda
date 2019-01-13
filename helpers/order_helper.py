import oandapy
from conf.config import Config
import oandapyV20
import oandapyV20.endpoints.orders as orders

class OrderHelper:
	def __init__(cls):
		cfg = Config()
		cls.account_id = cfg.get_oanda_env('account_id')
		cls.api_key = cfg.get_oanda_env('api_key')
		cls.environment = cfg.get_oanda_env('environment')
		cls.oanda = oandapy.API(environment=cls.environment, access_token=cls.api_key)
		cls.client = oandapyV20.API(access_token=cls.api_key)

	def create_order(cls, data):
		""" 
		Recieve a json data to create a new limit order.
		E.g:
		data = {
		  "order": {
		    "price": "1.2",
		    "stopLossOnFill": {
		      "timeInForce": "GTC",
		      "price": "1.22"
		    },
		    "timeInForce": "GTC",
		    "instrument": "EUR_USD",
		    "units": "-100",
		    "type": "LIMIT",
		    "positionFill": "DEFAULT"
		  }
		}
		"""
		r = orders.OrderCreate(cls.account_id, data=data)
		cls.client.request(r)



	def get_account_orders(cls):
		"""
		Get all orders fro the account.
		"""
		r = orders.OrderList(cls.account_id)
		return cls.client.request(r)


	def get_account_pending_orders(cls):
		"""
		Get all pending orders for the account.
		"""
		r = orders.OrdersPending(cls.account_id)
		return cls.client.request(r)

	def get_order_by_id(cls, order_id):
		"""
		Get details of a single order by given order_id
		"""
		r = orders.OrderDetails(accountID=cls.account_id, orderID=order_id)
		print cls.client.request(r)

	def cancel_pending_order(cls, order_id):
		"""
		Cancel a specific pending order by informed order_id
		"""
		r = orders.OrderCancel(accountID=cls.account_id, orderID=order_id)
		print cls.client.request(r)

