class Databank:
    def __init__(self):
        self.data = {
            "b11": [],
            "b12": [],
            "b21": ["123456"],
            "b22": ["123456"],
            "b31": ["Sealbot", "Labfellow", "p198573se1@sxwabw.al.net"],
            "b32": ["p198573se1@sxwabw.al.net"],
            "b41": ["Automated"],
            "b42": [],
            "b51": [],
            "b52": []
        }
        # "cate" : { "folder" : [ [fromElem, toElem],... ] }
        self.corresponding = {
            "b11": {
                "a11": [
                    ["acr.browser.lightning:id/search", "acr.browser.lightning:id/search"]
                ],
                "a12": [
                    ["org.easyweb.browser:id/main_title_url", "org.easyweb.browser:id/main_title_url"]
                ],
                "a13": [
                    ["com.stoutner.privacybrowser.standard:id/url_edittext",
                     "com.stoutner.privacybrowser.standard:id/url_edittext"]
                ],
                "a14": [
                    ["de.baumann.browser:id/main_omnibox_input", "de.baumann.browser:id/main_omnibox_input"]
                ],
                "a15": [
                    ["org.mozilla.focus:id/urlView", "org.mozilla.focus:id/display_url"]
                ]
            },
            "b12": {
                "a11": [
                    ["acr.browser.lightning:id/search", "acr.browser.lightning:id/search"]
                ],
                "a12": [
                    ["org.easyweb.browser:id/main_title_url", "org.easyweb.browser:id/main_title_url"]
                ],
                "a13": [
                    ["com.stoutner.privacybrowser.standard:id/url_edittext",
                     "com.stoutner.privacybrowser.standard:id/url_edittext"]
                ],
                "a14": [
                    ["de.baumann.browser:id/main_omnibox_input", "de.baumann.browser:id/main_omnibox_input"]
                ],
                "a15": [
                    ["org.mozilla.focus:id/urlView", "org.mozilla.focus:id/display_url"],
                    ["org.mozilla.focus:id/display_url", "org.mozilla.focus:id/display_url"]
                ]
            },
            "b21": {
                "a21": [
                    ["com.rubenroy.minimaltodo:id/userToDoEditText", "com.rubenroy.minimaltodo:id/toDoListItemTextview"]
                ],
                "a22": [
                    ["douzifly.list:id/edit_text", "douzifly.list:id/txt_thing"]
                ],
                "a23": [
                    ["org.secuso.privacyfriendlytodolist:id/et_new_task_name",
                     "org.secuso.privacyfriendlytodolist:id/tv_exlv_task_name"]
                ],
                "a24": [
                    ["kdk.android.simplydo:id/AddListEditText", "kdk.android.simplydo:id/text1"]
                ],
                "a25": [
                    ["com.woefe.shoppinglist:id/new_item_description", "com.woefe.shoppinglist:id/text_description"]
                ]
            },
            "b22": {
                "a21": [
                    ["com.rubenroy.minimaltodo:id/userToDoEditText", "com.rubenroy.minimaltodo:id/toDoListItemTextview"]
                ],
                "a22": [
                    ["douzifly.list:id/edit_text", "douzifly.list:id/txt_thing"]
                ],
                "a23": [
                    ["org.secuso.privacyfriendlytodolist:id/et_new_task_name",
                     "org.secuso.privacyfriendlytodolist:id/tv_exlv_task_name"]
                ],
                "a24": [
                    ["kdk.android.simplydo:id/AddListEditText", "kdk.android.simplydo:id/text1"]
                ],
                "a25": [
                    ["com.woefe.shoppinglist:id/new_item_description", "com.woefe.shoppinglist:id/text_description"]
                ]
            },
            "b31": {
                "a31": [
                    ["com.contextlogic.geek:id/create_account_fragment_first_name_text",
                     "com.contextlogic.geek:id/menu_profile_name"],
                    ["com.contextlogic.geek:id/create_account_fragment_last_name_text",
                     "com.contextlogic.geek:id/menu_profile_name"],
                    ["com.contextlogic.geek:id/create_account_fragment_first_name_text",
                     "com.contextlogic.geek:id/profile_fragment_header_name_text"]
                ],
                "a32": [
                    ["com.contextlogic.wish:id/create_account_fragment_first_name_text",
                     "com.contextlogic.wish:id/menu_profile_name"],
                    ["com.contextlogic.wish:id/create_account_fragment_last_name_text",
                     "com.contextlogic.wish:id/menu_profile_name"],
                    ["com.contextlogic.wish:id/create_account_fragment_first_name_text",
                     "com.contextlogic.wish:id/profile_fragment_header_name_text"]
                ],
                "a33": [
                    ["com.rainbowshops:id/text_email",
                     "com.rainbowshops:id/text_customer_email"],
                    ["com.rainbowshops:id/text_first_name",
                     "com.rainbowshops:id/text_customer_name"]
                ],
                "a35": [
                    ["com.yelp.android:id/first_name", "com.yelp.android:id/user_profile_name"]
                ]
            },
            "b32": {
                "a31": [],
                "a32": [],
                "a33": [
                    ["com.rainbowshops:id/text_username",
                     "com.rainbowshops:id/text_customer_email"]
                ],
                "a35": []
            },
            "b41": {
                "a41": [
                    ["android:id/search_src_text", "com.fsck.k9:id/subject"]
                ],
                "a42": [
                    ["android:id/search_src_text", "com.appple.app.email:id/subject"]
                ],
                "a43": [
                    ["ru.mail.mailapp:id/search_text", "ru.mail.mailapp:id/subject"]
                ],
                "a44": [
                    ["com.my.mail:id/search_text", "com.my.mail:id/subject"]
                ],
                "a45": [
                    ["park.outlook.sign.in.client:id/search_text", "park.outlook.sign.in.client:id/subject"]
                ]
            },
            "b42": {
                "a41": [
                    ["com.fsck.k9:id/subject", "com.fsck.k9:id/subject"]
                ],
                "a42": [
                    ["com.appple.app.email:id/subject", "com.appple.app.email:id/subject"]
                ],
                "a43": [
                    ["ru.mail.mailapp:id/subject", "ru.mail.mailapp:id/subject"],
                    ["ru.mail.mailapp:id/mailbox_create_new_body", "ru.mail.mailapp:id/snippet"]
                ],
                "a44": [
                    ["com.my.mail:id/subject", "com.my.mail:id/subject"],
                    ["com.my.mail:id/mailbox_create_new_body", "com.my.mail:id/snippet"]
                ],
                "a45": [
                    ["park.outlook.sign.in.client:id/subject", "park.outlook.sign.in.client:id/subject"],
                    ["park.outlook.sign.in.client:id/mailbox_create_new_body", "park.outlook.sign.in.client:id/snippet"]
                ]
            },
            "b51": {
                "a51": [],
                "a52": [],
                "a53": [],
                "a54": [],
                "a55": []
            },
            "b52": {
                "a51": [],
                "a52": [],
                "a53": [],
                "a54": [],
                "a55": []
            }
        }