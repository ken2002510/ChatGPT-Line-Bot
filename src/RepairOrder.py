from linebot.models import QuickReply, QuickReplyButton, MessageAction

def _quickreply(data):

    # elements = s.split(',')
    print(2)
   
    buttons = []
    for item in data:
        print(item)
        label = str(item.get('區域') + ","+item.get('案名') )
        text = str(item.get('地址'))
        print(label)
        button = QuickReplyButton(
            action=MessageAction(label=label, text=f'-!{label}')
        )
        buttons.append(button)
      
    # for element in elements:
    #     button = QuickReplyButton(
    #         action=MessageAction(label=element, text=element)
    #     )
    #     buttons.append(button)

  
    quickreply = QuickReply(items=buttons)
    print(quickreply)
    return quickreply
def checkdata():

    # elements = s.split(',')
    
    buttons = []
    button = QuickReplyButton(
            action=MessageAction(label='確定', text='資料無誤')
        )
    buttons.append(button)
    button = QuickReplyButton(
            action=MessageAction(label='修改', text='資料有錯誤')
        )
    buttons.append(button) 
    # for element in elements:
    #     button = QuickReplyButton(
    #         action=MessageAction(label=element, text=element)
    #     )
    #     buttons.append(button)

  
    quickreply = QuickReply(items=buttons)

    return quickreply
