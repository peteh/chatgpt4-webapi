import falcon
import json
from wsgiref import simple_server
import re
from decouple import config
from EdgeGPT import Chatbot, ConversationStyle
import asyncio

class ChatGPTResource(object):
    def __init__(self):
        #self._api = ChatGPT(auth_type='openai', email=openAIUser, password=openAIPass)
        self._conversationId = None

        self._api = Chatbot(cookiePath = "cookie.json")

    async def _summarize(self, prompt):

        response = await self._api.ask(prompt=prompt, conversation_style=ConversationStyle.creative, wss_link="wss://sydney.bing.com/sydney/ChatHub")
        text = response['item']['messages'][1]['text']
        #print(json.dumps(response['item']['messages'], indent =4))
        #await self._api.close()
        return {
            'text': text,
            'cost': 0
        }

    def on_post_completions(self, req, resp):
        prompt = req.media['prompt']

        if 'max_tokens' in req.media:
            numTokens = req.media['max_tokens']
            prompt += " - Answer in %d words or less! " % numTokens
        
        
        print("Prompt: " + prompt)
        chatResponse = {}
        chatResponse = asyncio.run(self._summarize(prompt))
        print(chatResponse)

        tokensPrompt = len(re.findall(r'\w+', prompt))
        tokensResponse = len(re.findall(r'\w+', chatResponse['text']))
        jsonResponse = {
                "id": "xxx",
                "object":"text_completion",
                "created":1670734183,
                "model":"text-davinci-003",
                "choices":[
                    {
                        'text': chatResponse['text'],
                        "index":0,
                        "logprobs":None,
                        "finish_reason":"stop"
                    }
                ],
                "usage":{
                    "prompt_tokens":tokensPrompt,
                    "completion_tokens":tokensResponse,
                    "total_tokens":tokensPrompt + tokensResponse
                }
            }
        resp.text = json.dumps(jsonResponse)

    async def reset(self):
        await self._api.reset()

    def on_get_reset(self, req, resp):
        asyncio.run(self.reset())
        self._conversationId = None
        jsonResponse = {'message': 'OK'}
        resp.text = json.dumps(jsonResponse)
    
    def on_get_refresh(self, req, resp):
        # TODO: this does nothing for now
        jsonResponse = {'message': 'OK'}
        resp.text = json.dumps(jsonResponse)
    
    def on_get_clear(self, req, resp):
        self._api.reset_chat()
        self._conversationId = None
        jsonResponse = {'message': 'OK'}
        resp.text = json.dumps(jsonResponse)


if __name__ == '__main__':
    api = falcon.App()
    chatGPTEndpoint = ChatGPTResource()
    api.add_route('/v1/completions', chatGPTEndpoint, suffix='completions')
    api.add_route('/v1/reset', chatGPTEndpoint, suffix='reset')
    api.add_route('/v1/refresh', chatGPTEndpoint, suffix='refresh')
    api.add_route('/v1/clear', chatGPTEndpoint, suffix='clear')

    try:
        httpd = simple_server.make_server('', 8001, api)
    except Exception as e:
        #logger.error(f"Couldn't start Server: {e}")
        #return 1
        exit(1)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()