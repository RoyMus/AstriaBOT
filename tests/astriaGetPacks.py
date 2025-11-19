import requests
import Utils.constants
headers = {'Authorization': f'Bearer {Utils.constants.ASTRIA_API_KEY}'}
response = requests.get('https://api.astria.ai/packs',headers=headers)

packs = response.json()

template_message = "Please choose a pack between the following options: "
for i, pack in enumerate(packs):
    template_message += f"\n{i + 1} - {pack['title']} - costs:"
    for key,value in pack['costs'].items():
        template_message+= f"\n {key} - {int(value['cost'])/100}$ for {value['num_images']} images"
    template_message += "\n"

print(template_message)