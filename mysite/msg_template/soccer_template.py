
def flex_soccer(self, Game_name, Team_name, Game_time, Game_one_score, Game_two_score, Game_animation_url):
    self.Game_name = Game_name
    self.Team_name = Team_name
    self.Game_time = Game_time
    self.Game_one_score = Game_one_score
    self.Game_two_score = Game_two_score
    self.Game_animation_url = Game_animation_url
    soccer_message = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "text",
                "text": self.Game_name,
                "weight": "bold",
                "size": "sm",
                "color": "#999999",
                "align": "start"
            },
            {
                "type": "box",
                "layout": "baseline",
                "margin": "md",
                "contents": [
                {
                    "type": "text",
                    "text": self.Team_name,
                    "size": "md",
                    "margin": "none",
                    "flex": 0,
                    "weight": "bold"
                }
                ]
            },
            {
                "type": "box",
                "layout": "vertical",
                "margin": "lg",
                "spacing": "sm",
                "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "text",
                        "text": "第一局",
                        "color": "#aaaaaa",
                        "size": "sm",
                        "flex": 1
                    },
                    {
                        "type": "text",
                        "text": self.Game_one_score,
                        "color": "#666666",
                        "size": "sm",
                        "flex": 5,
                        "align": "center",
                        "weight": "bold"
                    }
                    ]
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "text",
                        "text": "第二局",
                        "color": "#aaaaaa",
                        "size": "xs",
                        "flex": 1
                    },
                    {
                        "type": "text",
                        "text": self.Game_two_score,
                        "wrap": True,
                        "color": "#666666",
                        "size": "sm",
                        "flex": 5,
                        "align": "center",
                        "weight": "bold"
                    }
                    ]
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                    {
                        "type": "text",
                        "text": self.Game_time,
                        "margin": "none",
                        "size": "xs",
                        "weight": "bold"
                    }
                    ],
                    "spacing": "none",
                    "margin": "md"
                }
                ]
            }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
            {
                "type": "spacer"
            },
            {
                "type": "button",
                "style": "primary",
                "height": "sm",
                "action": {
                "type": "uri",
                "label": "動畫直播",
                "uri": self.Game_animation_url
                },
                "color": "#905c44"
            }
            ],
            "flex": 0
            }
        }
    
    return soccer_message