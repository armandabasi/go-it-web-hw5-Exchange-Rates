## _Exchange-Rates_

- This console utility allows you to get the exchange rate of cash currencies USD and EUR of PrivatBank for the past few days, as well as additional currencies that can be specified as parameters in the console.
- The utility follows the restriction that information about the exchange rate can be obtained for no more than the last 10 days. The utility uses Aiohttp client to access the Public API of PrivatBank and the National Bank of Ukraine.
- Also, the functionality of entering the "exchange" command in WebSocket chats to view the current currency exchange rate in text format has been implemented. 


- To launch the utility in the console, use the ```main.py``` file.
- To use WebSocket, use the ```web_socket.py``` file.

## To run the utility, use the following command in the console: 

```
py .\main.py -d <number> -c <comma-separated> list of currencies
```
Where:

• ```<number>```  - the number of days for which you need to get the exchange rate. Limitation - no more than 10 days.

• ```<comma-separated list of currencies>``` - a list of currencies whose exchange rate needs to be obtained. For example: USD,EUR.

## Instructions for using the "exchange" command in WebSocket chats:

- To display the current currency exchange rate in text format, enter the "exchange" command in the WebSocket chat.
- To display the currency exchange rate for the past few days, enter the "exchange " command in the WebSocket chat. For example: ```exchange 2```.


Additionally, the utility maintains a log file with data on the execution time of the "exchange" command in the chat. For this purpose, the aiofile and aiopath packages are used. The log file is saved in the current directory with the name ```data.json```.
