css = '''
<style>

iframe {
    position: fixed;
    left: 95%;
    bottom: 4.9%;
    width: 5%;
    z-index: 1;
    transform: scale(0.70);
}

.cover-glow {
    width: 100%;
    height: auto;
    padding: 3px;
    position: relative;
    border-radius: 30px;  /* Rounded corners */
}

.chat-message {
    padding: 1.5rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
}

.chat-message.user {
    background-color: #2b313e;
}

.chat-message.bot {
    background-color: #475063;
}

.chat-message .message {
    color: #fff;
    max-width: 80%;
}

</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="message">{{MSG}}</div>
</div>
'''
