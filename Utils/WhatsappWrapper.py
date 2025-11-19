import asyncio
from Utils import constants, states,message_ids
from Utils.WhatsappClient import WhatsappClient

class WhatsappWrapper:
    def __init__(self,phone_number,language : states.Languages = states.Languages.ENGLISH.value):
        self.client = None
        self.language = language
        self.phone_number = phone_number

    async def __aenter__(self):
        if self.client is None:
            self.client = await WhatsappClient().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client is not None:
            await self.client.__aexit__(None, None, None)
            self.client = None
    async def send_typing_indicator(self,message_id :str):
        if self.client is None:
            return
        await self.client.send_typing_indicator(self.phone_number,message_id)
    async def send_image_to_client(self, phone_number, image_path):
        if self.client is None:
            return
        await self.client.send_image_to_client(phone_number, image_path)
    async def send_invalid_media_message(self):
        if self.client is None:
            return
        if self.language == states.Languages.ENGLISH.value:
            response_message = "Hi!😊 Currently, I can only work with images.\n Other files (like videos, documents, links, etc.) are not supported."
        else:
            response_message = "היי!😊 כרגע אני מסוגל לעבוד עם תמונות בלבד.\n קבצים אחרים(כמו סרטונים, מסמכים, קישורים וכו') לא נתמכים."
        await self.client.send_message_to_client(self.phone_number, response_message)

    async def send_tunes_to_client(self, tunes):
        if self.client is None:
            return
        if self.language == states.Languages.ENGLISH.value:
            response_message = "Choose your model:"
            title = "Type: {name}"
            tune_template = "*Created at*: {created_at} \n" \
            "*Expires at*: {expires_at}"
            button_text = "use this model"
            no_models = "No models available at the moment, please try again later"
        else:
            response_message = "בחר את המודל שלך:"
            title = "סוג: {name}"
            tune_template = "*נוצר בתאריך*: {created_at} \n" \
            "*פג תוקף בתאריך*: {expires_at}"
            button_text = "השתמש במודל הזה"
            no_models = "אין מודלים זמינים כרגע, אנא נסה שוב מאוחר יותר"
        
        await self.client.send_message_to_client(self.phone_number, response_message)
        if len(tunes) == 0:
            await self.client.send_message_to_client(self.phone_number, no_models)
            return
        for tune in tunes:
            tune_message = tune_template.format(
                name=tune.get("name"),
                created_at=tune.get("created_at"),
                expires_at=tune.get("expires_at")
            )
            title_message = title.format(name=tune.get("name"))
            await self.client.send_interactive_reply_message(self.phone_number, tune_message, f"{message_ids.SET_TUNE}_{tune['id']}", button_text,title_message)

    async def send_returning_customer_msg(self):
        if self.client is None:
            return

        if self.language == states.Languages.ENGLISH.value:
            response_message = "I noticed that you have saved models.\n" \
            "Would you like to use one of the saved models or create a new model?"
            title = "Welcome back! 👋"
            I_want_button = "Show saved models"
            I_want_button2 = "New model"

        else:
            response_message = "שמתי לב שיש לך מודלים שמורים.\n" \
            "האם תרצה להשתמש באחד המודלים השמורים או ליצור מודל חדש?"
            title = "ברוך שובך! 👋"
            I_want_button = "הצג מודלים שמורים"
            I_want_button2 = "מודל חדש"
        
        await self.client.send_interactive_reply_message(self.phone_number,response_message,message_ids.SEND_TUNES,I_want_button,title,additional_button_id=message_ids.OVERRIDE_TUNE,additional_button_text=I_want_button2)
    async def send_init_msg(self):
        if self.client is None:
            return
        
        if self.language == states.Languages.ENGLISH.value:
            response_message = "Hi" + "! 👋 " + "I’m here to help you create stunning headshots using AI.\n"\
                            "Let’s start with a quick step of uploading images – I’m here for you every step of the way"
            response_message2 = "Options"
            option1 = "Let's begin!"
            option2 = "How it works"
            option3 = "Change to hebrew"
            option4 = "Contact support"
        else:
            response_message = "היי" + "! 👋 " + "אני כאן כדי לעזור לך ליצור תמונות תדמית מהממות בעזרת בינה מלאכותית.\n"\
                            "נתחיל עם שלב קצר של העלאת תמונות - אני איתך בכל צעד"
            response_message2 = "אופציות"
            option1 = "יאללה, נתחיל!"
            option2 = "איך זה עובד?"
            option3 = "החלף לאנגלית"
            option4 = "צור קשר עם תמיכה"
        options = {message_ids.BEGIN_REPLY: option1,message_ids.HOW_IT_WORKS:option2,message_ids.CHANGE_LANGUAGE:option3,message_ids.CONTACT_SUPPORT:option4}
        await self.client.send_interactive_list_message(self.phone_number, "", response_message,"PicMeAI",response_message2,options)

    async def send_upload_images_request(self,first_time = True):
        if self.client is None:
            return

        if self.language == states.Languages.ENGLISH.value:
            response_message = f"Awesome! Please upload your images now {('minimum ' + str(constants.MAX_IMAGES_THRESHOLD) + ' images required') if first_time else ''}\n"
            if not first_time:
                response_message += "When you're done, send me another text message"
        else:
            response_message =  f"מעולה! אנא העלה את התמונות שלך עכשיו {('מזכירים לך- לפחות ' + str(constants.MAX_IMAGES_THRESHOLD) + ' תמונות') if first_time else ''}\n"
            if not first_time:
                response_message += "כשתסיים תשלח לי הודעת טקסט נוספת"
            
        await self.client.send_message_to_client(self.phone_number,response_message)
    async def send_additional_images_request(self):
        if self.client is None:
            return

        if self.language == states.Languages.ENGLISH.value:
            title = "Great! I have enough images to get started!"
            response_message = "Would you like to add more? It can improve the accuracy even more"
            button_text1 = "Yes!"
            button_text2 = "No, I'm done"
            button_text3 = "Reset images"
            button_text4 = "Contact support"
            options_text = "Options"
        else:
            title = "מעולה! יש לי מספיק תמונות כדי להתחיל!"
            response_message =  "רוצה להוסיף עוד? זה יכול לשפר את הדיוק אפילו יותר"
            button_text1 = "כן!"
            button_text2 = "לא, אני סיימתי"
            button_text3 = "אני רוצה תמונות אחרות"
            button_text4 = "צור קשר עם תמיכה"
            options_text = "אופציות"
        await self.client.send_interactive_list_message(self.phone_number, title, response_message,"",options_text,{message_ids.UPLOAD_MORE_IMAGES:button_text1,message_ids.SEND_PACKS:button_text2,message_ids.OVERRIDE_TUNE:button_text3,message_ids.CONTACT_SUPPORT:button_text4})

    async def send_howitworks_msg(self):
        if self.client is None:
            return
        
        if self.language == states.Languages.ENGLISH.value:
            response_message = "*How it works:*\n\n" \
                     "- Just upload your photos\n" \
                    "- I’ll train a personal model just for you\n" \
                    "- I’ll create your images in the style you choose\n" \
                    "- You’ll get your new, unique images\n" \
                    "- Your model is saved with us for 30 days, so you can use it whenever you want\n" \
                    "- And a little bonus: it also helps save resources and protect the environment 🌱"
            response_message2 = "Would you like to begin?"
            response_message3 = "Let's begin!"
            response_message4 = "Let's do this!"
                                    
        else:
            response_message = "*איך זה עובד:*\n\n" \
                   "- פשוט תעלה את התמונות שלך\n" \
                   "- אני אאמן מודל אישי במיוחד בשבילך\n" \
                   "- אצור את התמונות שלך לפי הסגנון שבחרת\n" \
                   "- תוכל לקבל את התמונות החדשות והמיוחדות שלך\n" \
                   "- המודל שלך נשמר אצלנו למשך 30 יום, כך שתוכל להשתמש בו מתי שתרצה\n" \
                   "- ובונוס קטן: זה גם תורם לחיסכון במשאבים ובשמירה על הסביבה 🌱"
            response_message2 = "האם תרצה להתחיל?"
            response_message3 = "בואו נתחיל!"
            response_message4 = "בואו נעשה את זה!"

        await self.client.send_message_to_client(self.phone_number, response_message)
        await self.client.send_interactive_reply_message(self.phone_number, response_message2,message_ids.BEGIN_REPLY,response_message3,response_message4)
    async def send_imageguidelines_msg(self):
        if self.client is None:
            return

        if self.language == states.Languages.ENGLISH.value:
            response_message = "To create the best results for you\n\n"\
            "✅ Please upload:\n"\
                f"- At least {constants.MAX_IMAGES_THRESHOLD} clear, high-quality face photos\n"\
                "- In natural or well-lit lighting\n"\
                "\n"\
                "❌ Do not upload photos that are:\n"\
                "- Blurry\n"\
                "- Dark\n"\
                "- With hats/sunglasses\n"\
                "- Heavily filtered\n"\
                "- Group photos"
            button_text1 = "I'm ready!"
            button_text2 = "Show me examples"
            title = "Ready to upload photos?"
        else:
            response_message = "כדי שאצור עבורך תוצאה הכי מדויקת\n\n"\
            "✅ יש להעלות:\n"\
            f"- לפחות {constants.MAX_IMAGES_THRESHOLD} תמונות פנים ברורות באיכות טובה \n"\
            "- בתאורה טבעית או מוארת \n"\
            "\n"\
            "❌אין להעלות תמונות:\n"\
            "- מטושטשות\n"\
            "- כהות\n"\
            "- עם כובע/משקפי שמש \n"\
            "- פילטרים מוגזמים \n"\
            "- תמונות קבוצתיות"
            button_text1 = "אני מוכן\ה!"
            button_text2 = "שלח לי תמונות לדוגמה"
            title = "מוכן\ה להעלות תמונות?"

        await self.client.send_message_to_client(self.phone_number, response_message)
        await self.client.send_interactive_reply_message(self.phone_number, title, message_ids.READY_FOR_IMAGE_UPLOAD, button_text1,"",additional_button_id=message_ids.SHOW_EXAMPLES,additional_button_text=button_text2)

    async def send_additional_guidelines_images(self):
        if self.client is None:
            return

        if self.language == states.Languages.ENGLISH.value:
            button_text = "I'm ready!"
            title = "Ready to upload photos?"
        else:
            button_text = "אני מוכן\ה!"
            title = "מוכן\ה להעלות תמונות?"

        await self.client.send_image_to_client(self.phone_number, constants.RECOMMENDED_PHOTOS)
        await self.client.send_image_to_client(self.phone_number, constants.IMAGE_GUIDE_URL)
        await self.client.send_interactive_reply_message(self.phone_number, title, message_ids.READY_FOR_IMAGE_UPLOAD, button_text,"")

    async def send_preimagesent_msg(self):
        if self.client is None:
            return

        if self.language == states.Languages.ENGLISH.value:
            response_message = "🎉 Done! Your new headshots are ready.\n Enjoy the new you:"

        else:
            response_message = "🎉 סיימנו! התמונות שלך מוכנות.\n תהנה מאתה החדש:"

        await self.client.send_message_to_client(self.phone_number, response_message)

    async def send_postimagesent_msg(self):
        if self.client is None:
            return

        if self.language == states.Languages.ENGLISH.value:
            rate_title = "Rate us"
            rate_message = "Wow🤩 Beautiful images! What do you think? 😊"
            rating = "Rating"
            response_message = "Amazing! Would you like to create another pack at a special price?"
            I_want_button = "I want it now!"
            title = "Create another pack"
        else:
            rate_title = "דרגו אותנו"
            rate_message = "וואו🤩 תמונות מדהימות! מה דעתך? 😊"
            rating = "דירוג"
            response_message = "יצא מדהים! תרצה ליצור חבילה נוספת במחיר מיוחד?"
            I_want_button = "אני רוצה!"
            title = "צור חבילה נוספת"


        await self.client.send_interactive_list_message(self.phone_number, rate_title, rate_message, "PicMeAI",rating, {f"{message_ids.STAR_RATING}_{i}":f"{i}⭐" for i in range(1,6)})
        await self.client.send_interactive_reply_message(self.phone_number,response_message,message_ids.SEND_PACKS,I_want_button,title)
    async def send_feedback_comment(self,send_poor_feedback:bool):
        if self.client is None:
            return
        if self.language == states.Languages.ENGLISH.value:
            response_message = "Your feedback has been recorded.\nThank you for your input!"
            feedback_comment_message = "We are sorry to hear that you didn't have a great experience 😞\nPlease let us know how we can improve"
        else:
            response_message = "תגובתך נרשמה במערכת.\nתודה על המשוב!"
            feedback_comment_message = "אנחנו מצטערים לשמוע שלא הייתה לך חוויה טובה 😞\nאנא ספר לנו איך נוכל להשתפר"
        if send_poor_feedback:
            await self.client.send_message_to_client(self.phone_number, feedback_comment_message)
        else:
            await self.client.send_message_to_client(self.phone_number, response_message)
    async def send_support_email(self):
        if self.client is None:
            return
        if self.language == states.Languages.ENGLISH.value:
            response_message = "If you need support or you want to request a new feature,\nplease contact our support team at biglovelettersai@outlook.com"
        else:
            response_message = "אם אתה זקוק לעזרה או שיש לך רעיונות נוספים לשיפור המוצר,\nאנא פנה לצוות התמיכה שלנו בכתובת biglovelettersai@outlook.com"
        await self.client.send_message_to_client(self.phone_number, response_message)

    async def send_processingimages_msg(self, timeLeft):
        if self.client is None:
            return
        if self.language == states.Languages.ENGLISH.value:
            days = "days"
            hours = "hours"
            minutes = "minutes"
            one_day = "one day"
            one_hour = "one hour"
        else:
            days = "ימים"
            hours = "שעות"
            minutes = "דקות"
            one_day = "יום אחד"
            one_hour = "שעה אחת"

        printDays = (str(timeLeft.days) + " " +days) if timeLeft.days > 1 else one_day if timeLeft.days == 1 else None
        printHours = (str(timeLeft.seconds // 3600) + " " + hours) if timeLeft.seconds // 3600 > 1 else one_hour if timeLeft.seconds // 3600 == 1 else None
        printMinutes = (str((timeLeft.seconds % 3600) // 60) + " "+ minutes)
        time = printDays if printDays is not None else printHours if printHours is not None else printMinutes

        if self.language == states.Languages.ENGLISH.value:
            response_text = "*Amazing! we’re kicking things off⚡*\n\n" \
                    f"You’ll get your new images within {time} 📸\n" \
                    "Can’t wait for you to see yourself at your very best!🤩\n\n" \
                    "Feel free to go about your day – I’ll send you a message as soon as everything’s ready!"

        else:
            response_text = "*מעולה! אני יוצא לדרך⚡*\n\n" \
                    f"תוך {time} אשלח לך את התמונות החדשות שלך 📸\n" \
                    "מחכה שתראה\י את עצמך מהצד הכי טוב שלך!🤩\n\n"\
                    "בינתיים אפשר ללכת לעשות דברים אחרים בכיף – ברגע שזה יהיה מוכן תקבל\י הודעה עם התמונות החדשות."

        await self.client.send_message_to_client(self.phone_number, response_text)
    async def send_user_agreement_msg(self):
        if self.client is None:
            return

        if self.language == states.Languages.ENGLISH.value:
            response_message = "Just before we continue! 😊\n"\
            "These images are created by AI 🤖 and might not look 100% like you.\n"\
            "They’re auto-generated — without human editing.\n"\
            "Therfore, some minor deviations or artifacts may appear.\n\n"\
            "Please confirm you understand and agree to this before we continue onto the payment."
            button_text = "I agree"
            title = "Terms of Use"
        else:
            response_message =  "לפני שנמשיך! 😊\n"\
            "התמונות האלה נוצרות על ידי בינה מלאכותית 🤖 ולא תמיד ייראו 100% כמוך.\n"\
            "הן נוצרות אוטומטית - ללא עריכה אנושית.\n"\
            "לכן יכולות להופיע סטיות קלות או תקלות.\n\n"\
            r"אנא אשר\י שאת\ה מבין\ה ומסכים\ה לכך לפני שנמשיך לתשלום."
            button_text = r"אני מסכים\ה"
            title = "תנאי שימוש"

        await self.client.send_interactive_reply_message(self.phone_number, response_message, message_ids.GET_PAYMENT_LINK, button_text,title)

    async def send_paymentreceived_msg(self, fullName):
        if self.client is None:
            return

        if self.language == states.Languages.ENGLISH.value:
            response_message = f"Thank you for your payment💸,\n {fullName}"

        else:
            response_message = f"תודה רבה על התשלום💸,\n {fullName}"



        await self.client.send_message_to_client(self.phone_number, response_message)

    async def send_missingcredits_msg(self, creds_missing):
        if self.client is None:
            return

        if self.language == states.Languages.ENGLISH.value:
            response_message = f"You're missing {creds_missing} credits!\n Please add credits via the following link"

        else:
            response_message = f"חסרים לך {creds_missing} קרדיטים!\nאנא הוסף קרדיטים דרך הקישור הבא"


        await self.client.send_message_to_client(self.phone_number, response_message)
        await self.send_paymentlink_msg()
    async def send_video_example(self, video_url):
        if self.client is None:
            return

        if self.language == states.Languages.ENGLISH.value:
            response_message = "Here are the video examples from your pack"
        else:
            response_message = "הנה דוגמאות הווידאו מהחבילה שלך"

        await self.client.send_whatsapp_video(self.phone_number, video_url, response_message)
    async def send_video_to_client(self, phone_number, video_url):
        if self.client is None:
            return
        await self.client.send_whatsapp_video(phone_number, video_url)
    async def send_pack_tiers_msg(self):
        if self.client is None:
            return
        if self.language == states.Languages.ENGLISH.value:
            title = "Choose Your AI Image Plan 🎨"
            response_message = \
            f"- *Lite* – 12 images for {constants.LITE_TIER_PRICE}$ (great for trying out)\n"\
            f"- *Standard* – 24 images for {constants.STANDARD_TIER_PRICE}$ (more variety, better value)\n"\
            f"- *Premium* – 40 images for {constants.PREMIUM_TIER_PRICE}$ (maximum images + best deal)\n\n"\
            "🚀 Choose the plan that matches your vision and let’s create something amazing:"
            tier_1 = "Lite Pack"
            tier_2 = "Standard Pack"
            tier_3 = "Premium Pack"
            options_text = "Options"
        else:
            title = "בחר את חבילת התמונות שלך 🎨"
            response_message = \
            f"- *חבילת בסיס* – 12 תמונות ב- {constants.LITE_TIER_PRICE}$ (מעולה לניסיון)\n"\
            f"- *חבילה סטנדרטית* – 24 תמונות ב- {constants.STANDARD_TIER_PRICE}$ (יותר מגוון, יותר משתלם)\n"\
            f"- *חבילת פרימיום* – 40 תמונות ב- {constants.PREMIUM_TIER_PRICE}$ (מקסימום תמונות + העסקה הטובה ביותר)\n\n"\
            "🚀 בחר את החבילה שמתאימה לחזון שלך ובוא ניצור משהו מדהים יחד:"
            tier_1 = "חבילת בסיס"
            tier_2 = "חבילה סטנדרטית"
            tier_3 = "חבילת פרימיום"
            options_text = "אופציות"
        await self.client.send_interactive_list_message(self.phone_number, title, response_message,"PicMeAI",options_text,{message_ids.LITE_PACK:tier_1,message_ids.STANDARD_PACK:tier_2,message_ids.PREMIUM_PACK:tier_3})

    async def send_prepacks_msg(self, packs, entity_type,price):
        if self.client is None:
            return

        if self.language == states.Languages.ENGLISH.value:
            template_message = "Choose the type of pack you want to create – and I'll take care of the rest 😊"
            choosetext = "I want this!"
            button_text2 = "Show me examples"

        else:
            template_message = "בחרו את סוג החבילה שתרצו ליצור – ואני כבר אדאג לכל השאר 😊"
            choosetext = "אני רוצה את זה!"
            button_text2 = "תראה לי דוגמאות"

        await self.client.send_message_to_client(self.phone_number, template_message)

        for pack in packs:
            pack_message = f"{pack['title']}"
            costs = pack["costs"].get(entity_type)
            if costs is None:
                continue
            if self.language == states.Languages.ENGLISH.value:
                pack_message += f"\ncosts {price}$ for {costs['num_images']} images\n"
            else:
                pack_message += f"\nעלות {price}$ עבור {costs['num_images']} תמונות\n"

            await self.client.send_interactive_reply_image(self.phone_number,pack["cover_url"], pack_message, pack["id"], choosetext, additional_button_id=f"{message_ids.SHOW_PACK_IMAGES}_{pack['id']}", additional_button_text=button_text2)

    async def send_paymentlink_msg(self,payment_link:str):
        if self.client is None:
            return

        if self.language == states.Languages.ENGLISH.value:
            title = "You're almost there! 😊"
            response_message = "To get started, all you need to do is complete the payment here\n\n"\
            "It's easy and simple, we promise! \n" \
            "Let's start creating something amazing together 🚀"
            button_text = "Pay Now"
            additional_message = "Please note that payment processing takes a few minutes, don't worry, we'll notify you as soon as it's done!"
        else:
            title = "כמעט סיימנו! 😊"
            response_message = " כדי שנוכל להתחיל, כל מה שנשאר זה להשלים את התשלום כאן\n\n"\
            "הכל קל ופשוט, מבטיחים! \n" \
            "בואו נתחיל ליצור משהו מדהים יחד 🚀"
            button_text = "שלם עכשיו"
            additional_message = "אנא שימו לב כי עיבוד התשלום לוקח כמה דקות, אל תדאגו, נודיע לכם ברגע שזה יסתיים!"


        await self.client.send_interactive_url(self.phone_number, title, response_message, "PicMeAI", button_text, f"{payment_link}?phone={self.phone_number}")
        await self.client.send_message_to_client(self.phone_number, additional_message)

    async def respond_to_user_image(self, message_id, reason):
        if self.client is None:
            return

        if self.language == states.Languages.ENGLISH.value:
            response_message = "Hmm, this image might not work so well...\n" \
                f"Reason: {reason}.\n\n" \
                "Try a different one – I’m here to help! 😊" \

        else:
            response_message = "התמונה הזו לא תעבוד כל כך...\n" \
                f"הסיבה: {reason}.\n\n" \
                "נסה תמונה אחרת. אני כאן! 😊\n" \

        await self.client.reply_to_message(self.phone_number,response_message, message_id)

    async def respond_to_user_need_help(self):
        if self.client is None:
            return

        if self.language == states.Languages.ENGLISH.value:
            response_message = f"Please contact us at\n" \
                f"info.bigloveletters@gmail.com"

        else:
            response_message = f"בבקשה פנו אלינו במייל-\n" \
                               f"info.bigloveletters@gmail.com"

        await self.client.send_message_to_client(self.phone_number, response_message)

    async def send_reaction_emoji(self, message_id, reaction_emoji):
        if self.client is None:
            return
        
        await self.client.send_reaction_message(self.phone_number, message_id,reaction_emoji)
    async def send_error_message(self):
        if self.client is None:
            return

        if self.language == states.Languages.ENGLISH.value:
            response_message = "Oops! Something went wrong on our end. 😞\nPlease try again"
        else:
            response_message = "אופס! משהו השתבש אצלנו. 😞\nאנא נסה שוב"

        await self.client.send_message_to_client(self.phone_number, response_message)

    async def get_whatsapp_image(self, mediaId):
        if self.client is None:
            return None

        image = await self.client.get_whatsapp_image(mediaId)
        return image

    def setLanguage(self, languageOfChoice):
        self.language = languageOfChoice

    def setNumber(self, phoneNumber):
        self.phone_number = phoneNumber
        
    def GetLanguage(self):
        if self.client is None:
            return None

        return self.language