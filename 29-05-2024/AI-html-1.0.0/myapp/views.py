import logging
from django.shortcuts import render, redirect
from .models import User, WorkSpace, Uploadfiles, Onboard, Admin_user, Pricing, Feedback
from django.conf import settings
from django.core.mail import send_mail
import random
import requests
import json
import openai
import os
from django.urls import reverse
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
from moviepy.video.fx.all import resize
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from gtts import gTTS
from django.core.files import File
from django.db.models import Count
from django.contrib import messages
import re
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import time

logging.basicConfig(level=logging.INFO)  # Set to logging.DEBUG for more detailed logs

PEXELS_API_KEY = "ypeI3O5kOBaEaADVqRmmxrd0E9JYkg8ztdRerqANZQLbPwLc4KfKXbj1"
# Replace with your OpenAI API key
API_KEY = "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"
openai.api_key = API_KEY  # Set the OpenAI API key

# Create your views here.
def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        # Generate a verification code (You may use a library like secrets for this)
        verification_code = random.randint(100000, 999999)
        email_from = settings.EMAIL_HOST_USER
        send_mail('Verification Code', f'Your verification code is: {verification_code}','nishid.patel@gmail.com', [email])
        verification_code_str = str(verification_code)
        integer_to_insert = random.randint(0, 9)
        modified_code_str = verification_code_str[:2] + str(integer_to_insert) + verification_code_str[2:]
        # Save the verification code somewhere associated with the user (like a separate model)
        # For simplicity, I'll just use the session for this example
        return render(request, 'verify_otp.html', {'email': email, 'otp': modified_code_str})
    return render(request, 'signup.html')


def verify_otp(request):
    email = request.POST['email']
    uotp = request.POST['uotp']
    newOtp = uotp[:2] + uotp[3:]
    print(newOtp)
    otp = request.POST['otp']
    if request.method == 'POST':
        if otp == newOtp:
            try:
                user = User.objects.get(email=request.POST['email'])
                user.pswd = otp
                user_pk = user.pk
                user.save()
                request.session['email'] = user.email
                return redirect(reverse('work_space', kwargs={'pk': user_pk}))
            except User.DoesNotExist:
                user = User.objects.create(
                        email=email,
                        pswd=otp,       
                        )
                user_pk = user.pk
                request.session['email'] = user.email
                print(f"Verify OTP : {request.session['email']}")
                return redirect(reverse('onboard', kwargs={'pk': user_pk}))
        else:
            msg1 = "OTP doesn't match!!!"
            return render(request, 'verify_otp.html', {'msg1': msg1,'email': email, 'otp':uotp})
    else:
        return render(request, 'verify_otp.html')
        
def onboard(request, pk):

    try:
        # Get the user based on the email in the session
        user = User.objects.get(email=request.session['email'])

    except:
        # Handle the case where the user does not exist
        return redirect('login')
    
    if request.method == "POST":
        try:
            # Use the user session variables to get the user
            user = User.objects.get(email=request.session['email'])
            user.name = request.POST['workspace_username']
            user.save()
            # Ensure that the user exists and get other form data
            workspace_username = request.POST['workspace_username']
            workspace_name = request.POST['workspace_name']

            # Create an Onboard instance associated with the user
            onboard = Onboard.objects.create(
                user=user,
                workspace_username=workspace_username,
                workspace_name=workspace_name
            )

            msg = "Welcome in AI Video"

            # Redirect to the work_space page after onboard details are submitted
            return redirect(reverse('work_space', kwargs={'pk': pk}))

        except Exception as e:
            msg1 = f"Error: {e}"
            return render(request, 'onboard.html', {'msg1': msg1})

    else:
        msg1 = "Give some perfect information for our reference."
        return render(request, 'onboard.html', {'msg1': msg1})

def resend_code(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        verification_code = random.randint(100000, 999999)
        email_from = settings.EMAIL_HOST_USER
        send_mail('Verification Code', f'Your verification code is: {verification_code}', 'nishid.patel@gmail.com', [email])
        verification_code_str = str(verification_code)
        integer_to_insert = random.randint(0, 9)
        modified_code_str = verification_code_str[:2] + str(integer_to_insert) + verification_code_str[2:]
        return JsonResponse({'message': 'Verification code resent.', 'new_otp': modified_code_str})
    return JsonResponse({'message': 'Invalid request'}, status=400)        

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        # Generate a verification code (You may use a library like secrets for this)
        verification_code = random.randint(100000, 999999)
        email_from = settings.EMAIL_HOST_USER
        send_mail('Verification Code', f'Your verification code is: {verification_code}', 'nishid.patel@gmail.com', [email])
        verification_code_str = str(verification_code)
        integer_to_insert = random.randint(0, 9)
        modified_code_str = verification_code_str[:2] + str(integer_to_insert) + verification_code_str[2:]
        # Save the verification code somewhere associated with the user (like a separate model)
        # For simplicity, I'll just use the session for this example
        return render(request, 'verify_otp.html', {'email': email, 'otp': modified_code_str})
    return render(request, 'login.html')

def logout(request):
    if 'email' in request.session:
       del request.session['email']
    return redirect('login')

def generate_text(request, user_input_text, Eden_AI):
    headers = {"Authorization": f"Bearer {Eden_AI}"}
    url = "https://api.edenai.run/v2/text/generation"
    payload = {
        "providers": "openai,cohere",
        "text": user_input_text,
        "temperature": 0.2,
        "max_tokens": 2000
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        generated_text = result.get('cohere', {}).get('generated_text', None)
        if generated_text:
            return generated_text.replace("#", "").replace("*", "")
        else:
            print("Error: Unable to fetch generated text from Eden AI.")
            return None
    except requests.exceptions.RequestException as e:
        error_message = "There was an issue generating text. Please try again later."
        return render(request, 'error_page.html', {'error_message': error_message})


def generate_shorts_text(user_input_text, Eden_AI):
    headers = {"Authorization": f"Bearer {Eden_AI}"}
    url = "https://api.edenai.run/v2/text/generation"
    payload = {
        "providers": "google",
        "model": "gemini-pro",
        "text": user_input_text,
        "temperature": 0.1,
        "max_tokens": 120
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        generate_text = result.get('google', {}).get('generated_text', None)
        if generate_text:
            generated_text = generate_text.replace("#", "").replace("*", "")
            sentences = generated_text.split(".")
            # Remove the last incomplete sentence
            if not sentences[-1].endswith("."):
                generated_text = ". ".join(sentences[:-1])
            return generated_text
        else:
            print("Error: Unable to fetch generated text from Eden AI.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error in text generation process: {e}")
        return None
    
def create_folder(user_input_text):
    # Replace spaces with underscores
    folder_name = user_input_text.replace(" ", "_")
    base_folder_path = os.path.join(settings.MEDIA_ROOT, folder_name)

    # Check if the folder already exists
    if not os.path.exists(base_folder_path):
        os.makedirs(base_folder_path, exist_ok=True)
        return base_folder_path

    # If the folder already exists, append a suffix
    suffix = 1
    while True:
        folder_path = os.path.join(
            settings.MEDIA_ROOT, f"{folder_name}_{suffix}")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            return folder_path
        suffix += 1

def merge_videos(video_urls, folder_path, target_duration):
    video_clips = []
    common_width, common_height = None, None
    total_duration = 0

    while total_duration < target_duration:
        for i, video_url in enumerate(video_urls):
            if i >= 11 or total_duration >= target_duration:
                break

            video_response = requests.get(video_url, timeout=10)
            video_response.raise_for_status()
            video_filename = os.path.join(folder_path, f"output_video_{i + 1}.mp4")
            # video_file_name = os.path.basename(video_url).split('?')[0]
            video_file_path = os.path.join(folder_path, video_filename)

            with open(video_file_path, "wb") as f:
                f.write(video_response.content)

            video_clip = VideoFileClip(video_file_path)
            if common_width is None and common_height is None:
                common_width, common_height = video_clip.size
            video_clip_resized = video_clip.resize((common_width, common_height))
            video_clips.append(video_clip_resized)

            total_duration += video_clip.duration

    # Trim the last video clip to match the target duration
    if total_duration > target_duration:
        last_clip_duration = video_clips[-1].duration
        excess_duration = total_duration - target_duration
        trimmed_last_clip = video_clips[-1].subclip(0, last_clip_duration - excess_duration)
        video_clips[-1] = trimmed_last_clip

    merged_video_path = os.path.join(folder_path, "merged_video.mp4")

    try:
        final_clip = concatenate_videoclips(video_clips, method="compose")
        final_clip.write_videofile(
            merged_video_path, codec="libx264", fps=24, logger=None
        )
    except Exception as e:
        print(f"Error merging videos: {e}")
        raise

    return merged_video_path


def merge_audio_and_video(audio_path, video_path, output_path):
    audio_clip = AudioFileClip(audio_path)
    video_clip = VideoFileClip(video_path)
    # Ensure audio duration matches or is shorter than video duration
    audio_duration = min(audio_clip.duration, video_clip.duration)
    audio_clip = audio_clip.subclip(0, audio_duration)
    # Set the duration of the video clip to match the audio duration
    video_clip = video_clip.set_duration(audio_duration)
    # Combine audio and video
    final_clip = video_clip.set_audio(audio_clip)
    # Write the merged audio and video to a file
    final_clip.write_videofile(
        output_path, codec="libx264", fps=24, logger=None)
    return output_path

def generate_audio(text, folder_path, gender, Eden_AI):

    url = f"https://api.edenai.run/v2/audio/text_to_speech"

    headers = {"Authorization": f"Bearer {Eden_AI}"}

    payload = {
        "providers": "google",
        "language": "en-US",
        "option": "FEMALE",  # Change this to "MALE" or "FEMALE" as needed
        "text": text,
        "settings": {'google': f'{gender}' , 'amazon': 'en-US_Ivy_Standard'}
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        result = json.loads(response.text)
        google_audio_url = result['google']['audio_resource_url']
        audio_response = requests.get(google_audio_url)
        audio_data = audio_response.content
        print(folder_path)
        if 'mp3' in folder_path:
            audio_output_path = folder_path
        else:
           audio_output_path = os.path.join(folder_path, "output.mp3")

        with open(audio_output_path, 'wb') as audio_file:
            audio_file.write(audio_data)

        return audio_output_path

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def keyword_extraction(user_input_text, Eden_AI):
    headers = {"Authorization": f"Bearer {Eden_AI}"}

    url = "https://api.edenai.run/v2/text/keyword_extraction"
    payload = {
        "providers": "amazon,microsoft",
        "language": "en",
        "text": user_input_text
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.text)  # or use logging

    result = json.loads(response.text)

    # Extract keywords from the 'items' list for each provider
    keywords = [item['keyword'] for provider_data in result.values() if 'items' in provider_data for item in provider_data['items']]

    # Remove duplicates by converting the list to a set and back to a list
    unique_keywords = list(set(keywords))

    return unique_keywords

def get_three_min_video_from_pexels(user_input_text):
    try:
        api_key = 'ny88hc8urgf857vganyqsfqf'
        api_secret = 'jJTfqEMmCpuja7XYejV4'

        base_url = 'https://api.gettyimages.com'
        endpoint = '/v3/search/videos/creative'

        headers = {
            'Api-Key': api_key,
            'Api-Secret': api_secret,
        }
        params = {
            'phrase': user_input_text,
            'page': 1,
            'page_size': 10,
            'min_clip_length': 20
        }
        url = f'{base_url}{endpoint}'
        response = requests.get(url, headers=headers, params=params)

        response.raise_for_status()
        data = response.json()

        # Extract 'preview' URIs
        preview_uris = [size['uri'] for video in data.get('videos', []) for size in video.get('display_sizes', []) if size.get('name') == 'preview']
        # print(preview_uris)
        return preview_uris[:10]  # Return all the available videos
    except requests.exceptions.RequestException as e:
        print(f"Error fetching videos from Pexels: {e}")
        return []
    
def get_three_min_video_from_istock(newprompt):
    try:
        api_key = 'ny88hc8urgf857vganyqsfqf'
        api_secret = 'jJTfqEMmCpuja7XYejV4'

        base_url = 'https://api.gettyimages.com'
        endpoint = '/v3/search/videos/creative'

        headers = {
            'Api-Key': api_key,
            'Api-Secret': api_secret,
        }
        params = {
            'phrase': newprompt,
            'page': 1,
            'page_size': 10,
            'min_clip_length': 10
        }
        url = f'{base_url}{endpoint}'
        response = requests.get(url, headers=headers, params=params)

        response.raise_for_status()
        data = response.json()

        # Extract 'preview' URIs
        preview_uris = [size['uri'] for video in data.get('videos', []) for size in video.get('display_sizes', []) if size.get('name') == 'preview']
        # print(preview_uris)
        return preview_uris[:5]  # Return all the available videos
    except requests.exceptions.RequestException as e:
        print(f"Error fetching videos from Pexels: {e}")
        return []

def get_shorts_from_pexels(user_input_text):
    try:
        api_key = 'ny88hc8urgf857vganyqsfqf'
        api_secret = 'jJTfqEMmCpuja7XYejV4'

        base_url = 'https://api.gettyimages.com'
        endpoint = '/v3/search/videos/creative'

        headers = {
            'Api-Key': api_key,
            'Api-Secret': api_secret,
        }
        params = {
            'phrase': user_input_text,
            'page': 1,
            'page_size': 10,
            'min_clip_length': 15,
            'aspect_ratios': ["9:16"] 
        }
        url = f'{base_url}{endpoint}'
        response = requests.get(url, headers=headers, params=params)

        response.raise_for_status()
        data = response.json()
        # Extract 'preview' URIs
        preview_uris = [size['uri'] for video in data.get('videos', []) for size in video.get('display_sizes', []) if size.get('name') == 'preview']
        # print(preview_uris)
        return preview_uris[:5]  # Return all the available videos
    except requests.exceptions.RequestException as e:
        print(f"Error fetching videos from Pexels: {e}")
        return []

def get_shorts_from_istock(prompt):
    try:
        api_key = 'ny88hc8urgf857vganyqsfqf'
        api_secret = 'jJTfqEMmCpuja7XYejV4'

        base_url = 'https://api.gettyimages.com'
        endpoint = '/v3/search/videos/creative'

        headers = {
            'Api-Key': api_key,
            'Api-Secret': api_secret,
        }
        params = {
            'phrase': prompt,
            'page': 1,
            'page_size': 10,
            'min_clip_length': 15,
            'aspect_ratios': ["9:16"] 
        }
        url = f'{base_url}{endpoint}'
        response = requests.get(url, headers=headers, params=params)

        response.raise_for_status()
        data = response.json()
        # Extract 'preview' URIs
        preview_uris = [size['uri'] for video in data.get('videos', []) for size in video.get('display_sizes', []) if size.get('name') == 'preview']
        # print(preview_uris)
        return preview_uris[:3]  # Return all the available videos
    except requests.exceptions.RequestException as e:
        print(f"Error fetching videos from Pexels: {e}")
        return []

def generate_audio_from_video(video_path, output_audio_path):
    try:
        video_clip = VideoFileClip(video_path)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(output_audio_path)
        video_clip.close()
        return output_audio_path
    except Exception as e:
        print(f"Error generating audio from video: {e}")
        return None

def split_video_into_segments_with_audio(video_path, output_folder, segment_duration=20):
    os.makedirs(output_folder, exist_ok=True)

    video_clip = VideoFileClip(video_path)
    total_duration = video_clip.duration
    num_segments = int(total_duration // segment_duration)

    segment_urls = []
    segment_audio_paths = []

    for i in range(num_segments):
        start_time = i * segment_duration
        end_time = (i + 1) * segment_duration
        segment = video_clip.subclip(start_time, end_time)

        segment_filename = f"segment_{i + 1}.mp4"
        segment_filepath = os.path.join(output_folder, segment_filename)
        segment.write_videofile(segment_filepath, codec="libx264", audio_codec="aac")

        # Generate audio from the video segment
        output_audio_path = os.path.join(output_folder, f"segment_{i + 1}.mp3")
        audio_path = generate_audio_from_video(segment_filepath, output_audio_path)
        
        if audio_path:
            # Construct the URL for the segment audio using MEDIA_URL
            relative_audio_path = os.path.relpath(audio_path, settings.MEDIA_ROOT)
            segment_audio_paths.append(os.path.join(settings.MEDIA_URL, relative_audio_path))

        # Construct the URL for the segment video using MEDIA_URL
        relative_path = os.path.relpath(segment_filepath, settings.MEDIA_ROOT)
        segment_urls.append(os.path.join(settings.MEDIA_URL, relative_path))

    # Handle the remaining duration
    remaining_duration = total_duration % segment_duration
    if remaining_duration > 0:
        start_time = num_segments * segment_duration
        remaining_segment = video_clip.subclip(start_time, total_duration)
        remaining_filename = f"segment_{num_segments + 1}.mp4"
        remaining_filepath = os.path.join(output_folder, remaining_filename)
        remaining_segment.write_videofile(
            remaining_filepath, codec="libx264", audio_codec="aac")

        # Generate audio from the remaining segment
        output_audio_path = os.path.join(output_folder, f"segment_{num_segments + 1}.mp3")
        audio_path = generate_audio_from_video(remaining_filepath, output_audio_path)

        if audio_path:
            # Construct the URL for the remaining segment audio using MEDIA_URL
            relative_audio_path = os.path.relpath(audio_path, settings.MEDIA_ROOT)
            segment_audio_paths.append(os.path.join(settings.MEDIA_URL, relative_audio_path))

        # Construct the URL for the remaining segment using MEDIA_URL
        relative_path = os.path.relpath(
            remaining_filepath, settings.MEDIA_ROOT)
        remaining_segment_url = os.path.join(settings.MEDIA_URL, relative_path)
        segment_urls.append(remaining_segment_url)

    video_clip.close()

    return segment_audio_paths

def split_video_into_segments(video_path, output_folder, segment_duration=20):
    os.makedirs(output_folder, exist_ok=True)

    video_clip = VideoFileClip(video_path)
    total_duration = video_clip.duration
    num_segments = int(total_duration // segment_duration)

    segment_urls = []

    for i in range(num_segments):
        start_time = i * segment_duration
        end_time = (i + 1) * segment_duration
        segment = video_clip.subclip(start_time, end_time)

        segment_filename = f"segment_{i + 1}.mp4"
        segment_filepath = os.path.join(output_folder, segment_filename)
        segment.write_videofile(
            segment_filepath, codec="libx264", audio_codec="aac")

        # Construct the URL for the segment using MEDIA_URL
        relative_path = os.path.relpath(segment_filepath, settings.MEDIA_ROOT)
        segment_url = os.path.join(settings.MEDIA_URL, relative_path)
        segment_urls.append(segment_url)

    # Handle the remaining duration
    remaining_duration = total_duration % segment_duration
    if remaining_duration > 0:
        start_time = num_segments * segment_duration
        remaining_segment = video_clip.subclip(start_time, total_duration)
        remaining_filename = f"segment_{num_segments + 1}.mp4"
        remaining_filepath = os.path.join(output_folder, remaining_filename)
        remaining_segment.write_videofile(
            remaining_filepath, codec="libx264", audio_codec="aac")

        # Construct the URL for the remaining segment using MEDIA_URL
        relative_path = os.path.relpath(
            remaining_filepath, settings.MEDIA_ROOT)
        remaining_segment_url = os.path.join(settings.MEDIA_URL, relative_path)
        segment_urls.append(remaining_segment_url)

    video_clip.close()

    return segment_urls

def transcribe_audio_to_text(audio_file_path):
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = openai.Audio.transcribe(
                file=audio_file,
                model="whisper-1",
                response_format="text",
                language="en",  # Use ISO-639-1 format for English
            )

            # Assuming response is a string containing the transcribed text
            transcript = response

            # Create a counter to generate unique filenames
            counter = 1

            # Save the transcript to a text file with a unique name
            while True:
                text_file_name = f"transcript_{counter}.txt"
                text_file_path = os.path.join(os.path.dirname(audio_file_path), text_file_name)
                if not os.path.exists(text_file_path):
                    break
                counter += 1

            with open(text_file_path, "w") as text_file:
                text_file.write(transcript)
            return text_file_path
    except Exception as e:
        print(f"Error transcribing audio to text: {e}")
        return None    

def work_space(request, pk):
    segment_urls = []
    segment_texts = []
    video_urls = []
    shorts_option_selected = False
    Eden_AI = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZGU3ZDdhZWUtNTZhYy00N2UwLWFlNzItNTI2MDkwYjE5NWJiIiwidHlwZSI6ImFwaV90b2tlbiJ9.XQ1Yttl3yCVRZQB1IAk9pHSX5hzB6vAlH7G07lpacDE"

    # Check if 'email' key is present in the session
    # if request.session['email']:
    #     # Handle the case where the user is not authenticated
    #     print("LULU")
    #     return redirect('login')

    try:
        # Get the user based on the email in the session
        user = User.objects.get(email=request.session['email'])
        # user = User.objects.get(email=request.session['email'])
        onboard = Onboard.objects.get(user=user)
        workspace_name = onboard.workspace_name

    except:
        # Handle the case where the user does not exist
        return redirect('login')
    if pk is None:
        # Redirect to an error page or display an error message
        return redirect('index')

    if request.method == 'POST':

        user_pricing = Pricing.objects.filter(user=user).first()
        # Check if the user has any pricing data

        if user_pricing:
            user_plan_end_date = user_pricing.end_date
            today_date = datetime.now().date()
            if user_plan_end_date == today_date:
                name_of_plan = "Free"
            else:
                price_of_plan = user_pricing.price_of_plan
                if price_of_plan == 500:
                    name_of_plan = "Max Yearly"
                elif price_of_plan == 200:
                    name_of_plan = "Plus Yearly"
                elif  price_of_plan == 55:
                    name_of_plan = "Max Monthly"    
                elif  price_of_plan == 25:
                    name_of_plan = "Plus Monthly"
        else:
            name_of_plan = "Free"


        user_input_texts = request.POST.get('message', '')
        user_input_text = re.sub(r'[?/!#\$]', '', user_input_texts)
        new_prompt = keyword_extraction(user_input_text, Eden_AI)
        number_of_elements = len(new_prompt)
        selected_option = request.POST.get('youtube-option')
        if selected_option == "explainer":
            generated_text = generate_text(request, user_input_text, Eden_AI)
        elif selected_option == "shorts":
            generated_text = generate_shorts_text(user_input_text, Eden_AI)

        #text is generated or not
        if generated_text:
            sentences = generated_text.split('.')
            for i in range(0, len(sentences), 5):
                group = '.'.join(sentences[i:i+5])
                segment_texts.append(group)
            segment_texts = [text.replace("\n", "")+'.' for text in segment_texts]
            #text is divided into segments or not
            if segment_texts:
                folder_path = create_folder(user_input_text)
                if selected_option == "explainer":
                    if number_of_elements > 1:
                        video_urls = [url for prompt in new_prompt for url in get_three_min_video_from_istock(prompt)]
                    else:
                        video_urls = get_three_min_video_from_pexels(user_input_text)
                elif selected_option == "shorts":
                    shorts_option_selected = True
                    if number_of_elements > 1:
                        video_urls = [url for prompt in new_prompt for url in get_shorts_from_istock(prompt)]
                    else:
                        video_urls = get_shorts_from_pexels(user_input_text)

                #video are fetched or not from istock
                if video_urls:
                    gender = request.POST.get('gender', '')
                    generated_audio_path = generate_audio(generated_text, folder_path, gender, Eden_AI)
                    
                    #audio is generated or not
                    if generated_audio_path:
                        # Initialize merged_audio_and_video_path to None
                        merged_audio_and_video_path = None

                        # Handle file upload
                        # uploaded_file = request.FILES.get('file_upload')
                        # if uploaded_file:
                        #     # Save the uploaded file to a specific folder
                        #     file_path = os.path.join(folder_path, uploaded_file.name)
                        #     default_storage.save(file_path, ContentFile(uploaded_file.read()))
                        #     # Now, you can use 'file_path' as needed


                        # Save the generated text and video URL to the WorkSpace model
                        work_space_entry = WorkSpace.objects.create(
                            user=user,
                            message=user_input_text,
                            gender=gender,
                            generated_text=generated_text,
                            video_url=merged_audio_and_video_path  # Change this to the actual video URL
                        )

                        target_duration = 180
                        merged_video_path = merge_videos(video_urls, folder_path, target_duration)
                        
                        #merging video
                        if merged_video_path:
                            # Merge audio and video
                            output_path = os.path.join(folder_path, f"{user_input_text}.mp4")
                            merged_audio_and_video_path = merge_audio_and_video(generated_audio_path, merged_video_path,
                                                                                output_path)
                            relative_path = os.path.relpath(merged_audio_and_video_path, settings.MEDIA_ROOT)
                            
                            #merging video or audio
                            if merged_audio_and_video_path:
                                output_folder = os.path.join(folder_path, 'video_segments')
                                segment_urls = split_video_into_segments(
                                    merged_audio_and_video_path, output_folder, segment_duration=20)
                                segment_audio_urls = split_video_into_segments_with_audio(
                                    merged_audio_and_video_path, output_folder, segment_duration=20)

                                #segmented into texts and urls   
                                if segment_urls and segment_texts:

                                    upload_files_entry = Uploadfiles.objects.create(
                                        user=user,
                                        workspace=work_space_entry,
                                        segment_url_1=segment_urls[0] if segment_urls and len(segment_urls) > 0 else None,
                                        segment_url_2=segment_urls[1] if segment_urls and len(segment_urls) > 1 else None,
                                        segment_url_3=segment_urls[2] if segment_urls and len(segment_urls) > 2 else None,
                                        segment_url_4=segment_urls[3] if segment_urls and len(segment_urls) > 3 else None,
                                        segment_url_5=segment_urls[4] if segment_urls and len(segment_urls) > 4 else None,
                                        segment_url_6=segment_urls[5] if segment_urls and len(segment_urls) > 5 else None,
                                        segment_url_7=segment_urls[6] if segment_urls and len(segment_urls) > 6 else None,
                                        segment_url_8=segment_urls[7] if segment_urls and len(segment_urls) > 7 else None,
                                        segment_url_9=segment_urls[8] if segment_urls and len(segment_urls) > 8 else None,
                                        segment_text_1=segment_texts[0] if segment_texts and len(segment_texts) > 0 else None,
                                        segment_text_2=segment_texts[1] if segment_texts and len(segment_texts) > 1 else None,
                                        segment_text_3=segment_texts[2] if segment_texts and len(segment_texts) > 2 else None,
                                        segment_text_4=segment_texts[3] if segment_texts and len(segment_texts) > 3 else None,
                                        segment_text_5=segment_texts[4] if segment_texts and len(segment_texts) > 4 else None,
                                        segment_text_6=segment_texts[5] if segment_texts and len(segment_texts) > 5 else None,
                                        segment_text_7=segment_texts[6] if segment_texts and len(segment_texts) > 6 else None,
                                        segment_text_8=segment_texts[7] if segment_texts and len(segment_texts) > 7 else None,
                                        segment_text_9=segment_texts[8] if segment_texts and len(segment_texts) > 8 else None,
                                    )
                                    # Update the WorkSpace model with the actual video URL
                                    work_space_entry.video_url = os.path.join(settings.MEDIA_URL, relative_path)
                                    work_space_entry.upload_files_entry = upload_files_entry
                                    work_space_entry.save()

                                    user_work_space_entries = WorkSpace.objects.filter(user=user)
                                    return render(request, 'work_space.html', {
                                        'pk': pk,
                                        'user': user,
                                        'generated_text': generated_text,
                                        'generated_audio_path': generated_audio_path,
                                        'video_urls': video_urls,
                                        'user_input_text': user_input_text,
                                        'work_space_entry': work_space_entry,
                                        # 'video_filenames': video_filenames,
                                        'merged_video_path': merged_video_path,
                                        'merged_audio_and_video_path': os.path.join(settings.MEDIA_URL, relative_path),
                                        'user_work_space_entries': user_work_space_entries,
                                        'segment_urls': segment_urls,
                                        'segment_texts': segment_texts,  # Pass user's WorkSpace entries to the template
                                        'workspace_name': workspace_name,
                                        'name_of_plan' : name_of_plan,
                                        'shorts_option_selected': shorts_option_selected,

                                    })
                                else:
                                    error_message = "There was an issue segmented video and text. Please try again later."
                                    return render(request, 'error_page.html', {'error_message': error_message, 'pk': pk})
                            else:
                                error_message = "There was an issue merged video with audio. Please try again later."
                                return render(request, 'error_page.html', {'error_message': error_message, 'pk': pk})
                        else:
                            error_message = "There was an issue merged video. Please try again later."
                            return render(request, 'error_page.html', {'error_message': error_message, 'pk': pk})
                    else:
                        error_message = "There was an issue audio. Please try again later."
                        return render(request, 'error_page.html', {'error_message': error_message, 'pk': pk})
                else:
                    error_message = "There was an issue Video URLS. Please try again later."
                    return render(request, 'error_page.html', {'error_message': error_message, 'pk': pk}) 
            else:
                error_message = "There was an issue Segmented text. Please try again later."
                return render(request, 'error_page.html', {'error_message': error_message, 'pk': pk})
        else:
            error_message = "There was an issue generating text. Please try again later."
            return render(request, 'error_page.html', {'error_message': error_message, 'pk': pk})
    else:
        user_work_space_entries = WorkSpace.objects.filter(user=user)
        user_pricing = Pricing.objects.filter(user=user).first()
        # Check if the user has any pricing data

        if user_pricing:
            user_plan_end_date = user_pricing.end_date
            today_date = datetime.now().date()
            if user_plan_end_date == today_date:
                name_of_plan = "Free"
            else:
                price_of_plan = user_pricing.price_of_plan
                if price_of_plan == 500:
                    name_of_plan = "Max Yearly"
                elif price_of_plan == 200:
                    name_of_plan = "Plus Yearly"
                elif  price_of_plan == 55:
                    name_of_plan = "Max Monthly"    
                elif  price_of_plan == 25:
                    name_of_plan = "Plus Monthly"
        else:
            name_of_plan = "Free"

        return render(request, 'work_space.html', {
            'pk': pk,
            'user': user,
            'user_work_space_entries': user_work_space_entries,
            'workspace_name': workspace_name,
            'name_of_plan' : name_of_plan,
            
        })

def user_history(request, pk):
    # Your view logic goes here
    return render(request, 'user_history.html', {'pk': pk})

def save_feedback(request):
    if request.method == 'POST':
        feedback_message = request.POST.get('feedback_message')
        if feedback_message:
            if request.session['email']:
                user = User.objects.get(email=request.session['email'])
                Feedback.objects.create(user=user, message=feedback_message)
                return JsonResponse({'success': True, 'message': 'Feedback submitted successfully'})
            else:
                return JsonResponse({'success': False, 'message': 'User not authenticated'}, status=401)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

def delete_segment(request, workspace_pk, segment_index):
    if request.method == 'DELETE':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            segment_url = data.get('segment_url', '')

            workspace = get_object_or_404(WorkSpace, pk=workspace_pk)
            upload_file = get_object_or_404(Uploadfiles, workspace=workspace)

            # Determine the field name based on the segment index
            field_name = f'segment_url_{segment_index + 1}'

            # Get the current value of the field
            current_value = getattr(upload_file, field_name, None)

            if current_value == segment_url:
                # If the current value matches the provided URL, delete it
                setattr(upload_file, field_name, None)
                upload_file.save()

                return JsonResponse({'success': True, 'message': 'Segment deleted successfully'})
            else:
                return JsonResponse({'success': False, 'message': 'Segment URL does not match the record'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

def update_segment_texts(request, workspace_pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.POST.get('updated_texts', '{}'))
            workspace = get_object_or_404(WorkSpace, pk=workspace_pk)
            upload_file = get_object_or_404(Uploadfiles, workspace=workspace)

            for segment_index, segment_text in data.items():
                field_name = f'segment_text_{segment_index}'
                setattr(upload_file, field_name, segment_text)

            upload_file.save()

            return JsonResponse({'success': True, 'message': 'Segment texts updated successfully'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

def upload_video(request, pk):
    if request.method == 'POST':
        segment_number = int(pk)
        uploaded_file = request.FILES.get('video_upload')

        if uploaded_file:
            # Save the uploaded file to the corresponding field in the Uploadfiles model
            user = User.objects.get(email=request.session['email'])
            work_space_entry = WorkSpace.objects.filter(user=user).last()
            upload_files_entry = Uploadfiles.objects.filter(workspace=work_space_entry).last()

            # Determine the field name based on the segment number
            field_name = f'upload_video_{segment_number}'
            setattr(upload_files_entry, field_name, uploaded_file)
            upload_files_entry.save()
            
            url_field_name = f'segment_url_{segment_number}'
            setattr(upload_files_entry, url_field_name, '')
            upload_files_entry.save()

            return JsonResponse({'success': True, 'message': f'Video for Segment {segment_number} uploaded successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'No file uploaded'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}) 
        
def merge_uploaded_videos(workspace, user, static_prefix="/var/www/html/AI-html-1.0.0"):
    try:
        # Get the latest Uploadfiles entry associated with the workspace
        upload_files_entry = Uploadfiles.objects.filter(workspace=workspace).last()
        
        # Create a list to store VideoFileClip objects and text
        video_clips = []
        text_clips = []

        # Fetch video paths and text from the segment_url and segment_text fields
        for i in range(1, 10):
            field_url_name = f'segment_url_{i}'
            field_text_name = f'segment_text_{i}'
            field_name = f'upload_video_{i}'
            
            video_path = getattr(upload_files_entry, field_url_name, None)
            text = getattr(upload_files_entry, field_text_name, None)
            video_file = getattr(upload_files_entry, field_name, None)
            
            if video_path:
                # Add the static prefix to the video path
                video_path_with_prefix = static_prefix + video_path
                
                # Check if the file exists before creating VideoFileClip
                if os.path.exists(video_path_with_prefix):
                    filename = os.path.basename(video_path)
                    video_clip = VideoFileClip(video_path_with_prefix)
                    video_clips.append(video_clip)
                else:
                    print(f"File not found: {video_path_with_prefix}")

            elif video_file and os.path.exists(video_file.path):
                # Create VideoFileClip from the upload_video file
                video_clip = VideoFileClip(video_file.path)
                video_clips.append(video_clip)
            else:
                print(f"No video found in {field_name}")
            
            if text:
                text_clips.append(text)

        # Reset the text variable for the second loop
        text = None

        # Merge the text clips
        merged_text = "\n".join(text_clips)
        # Convert merged text to speech and save as audio file
        # tts = gTTS(text=merged_text, lang='en')

        audio_file_path = f'{static_prefix}/media/music/edited_audio.mp3'
        
        # Determine the output audio file path with index
        base_audio_file_path = audio_file_path.replace('.mp3', '')
        index = 1
        while os.path.exists(audio_file_path):
            audio_file_path = f"{base_audio_file_path}_{index}.mp3"
            index += 1

        # tts.save(audio_file_path)
        work_space_entry = WorkSpace.objects.filter(
                user=user
            ).last()
        gender= work_space_entry.gender

        audio_file_path = generate_audio(merged_text, audio_file_path, gender, Eden_AI = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZGU3ZDdhZWUtNTZhYy00N2UwLWFlNzItNTI2MDkwYjE5NWJiIiwidHlwZSI6ImFwaV90b2tlbiJ9.XQ1Yttl3yCVRZQB1IAk9pHSX5hzB6vAlH7G07lpacDE")
        # Load the audio file as an AudioFileClip
        audio_clip = AudioFileClip(audio_file_path)

        # Determine the duration of the audio and video
        audio_duration = audio_clip.duration
        video_duration = sum([clip.duration for clip in video_clips])

        # Extend or trim the video to match the audio duration
        num_loops = int(audio_duration / video_duration) + 1
        final_video_clips = video_clips * num_loops
        final_video = concatenate_videoclips(final_video_clips, method="compose")

        # Trim the final video to match the audio duration
        final_video = final_video.subclip(0, audio_duration)

        # Set the audio of the final video
        final_video = final_video.set_audio(audio_clip)

        # Determine the output video file path with index
        base_output_path = f'{static_prefix}/media/videos/edited_video'
        output_path = f"{base_output_path}.mp4"

        index = 1
        while os.path.exists(output_path):
            output_path = f"{base_output_path}_{index}.mp4"
            index += 1

        # Save the merged video to a file
        final_video.write_videofile(output_path, codec="libx264", fps=24, logger=None)
        relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
        segment_url = os.path.join(settings.MEDIA_URL, relative_path)
        work_space_entry = WorkSpace.objects.filter(
                user=user
            ).last()
        work_space_entry.edited_video_url = segment_url
        work_space_entry.save()
        # Save the video file to the edited_video field
        edited_video_file = open(output_path, "rb")
        upload_files_entry.edited_video.save(os.path.basename(output_path), File(edited_video_file))
        edited_video_file.close()
        
        # Return the path of the merged video
        return segment_url

    except Exception as e:
        print(f"Error merging uploaded videos: {e}")
        return None
        
def merge_edited_audio_video(request, pk):
    try:
        user = User.objects.get(email=request.session['email'])
        workspace = WorkSpace.objects.filter(user=user).last()

        # Call the function to merge uploaded videos
        merged_edited_video = merge_uploaded_videos(workspace, user)

        if merged_edited_video:
            # Pass the merged video path to the template
            return JsonResponse({'success': True, 'message': 'Videos merged successfully', 'merged_edited_video': merged_edited_video})
        else:
            return JsonResponse({'success': False, 'message': 'Error merging videos'})

    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User does not exist'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'})

def admin_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        pswd = request.POST.get('pswd')
        
        try:
            admin_user = Admin_user.objects.get(email=email, pswd=pswd)
            # Store user information in session if needed
            request.session['email'] = admin_user.email
            request.session['pswd'] = admin_user.pswd
            messages.success(request, 'Login successful')
            return redirect('admin_side')
        except Admin_user.DoesNotExist:
            messages.error(request, 'Invalid credentials. Please try again.')

    return render(request, 'admin_login.html')

def admin_side(request):
    # Check if email and password are present in the session
    if 'email' in request.session and 'pswd' in request.session:
        email = request.session['email']
        pswd = request.session['pswd']

        try:
            admin_user = Admin_user.objects.get(email=email, pswd=pswd)
            # Fetch the most common messages in WorkSpace
            most_common_messages = WorkSpace.objects.values('message').annotate(message_count=Count('message')).order_by('-message_count')[:5]
            most_common_message_qs = WorkSpace.objects.values('message').annotate(message_count=Count('message')).order_by('-message_count')[:1]
            most_common_message = most_common_message_qs[0]['message']
            total_user_count = User.objects.count()
            total_video_count = WorkSpace.objects.count()
            video_name = WorkSpace.objects.all()
            users_with_video_count = User.objects.annotate(video_count=Count('workspace'))
            all_users_with_messages = User.objects.annotate(message_count=Count('workspace__message'))
            context = {
                'total_user_count': total_user_count,
                'total_video_count': total_video_count,
                'video_name': video_name,
                'users_with_video_count': users_with_video_count,
                'all_users_with_messages': all_users_with_messages,
                'most_common_messages': most_common_messages,
                'most_common_message' : most_common_message,
            }
            return render(request, 'admin_side.html', context)
        except Admin_user.DoesNotExist:
            # Handle the case when the Admin_side is not found
            pass

    # If email and password are not present in the session or Admin_side is not found, redirect to login
    return redirect('admin_login')

def admin_logout(request):
    if 'email' in request.session:
        del request.session['email']
    return redirect('admin_login')

def delete_entry(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(pk=user_id)
            user.delete()
            # Redirect to admin side view after deletion
            return redirect('admin_side')
        except User.DoesNotExist:
            pass
    # Handle if the user does not exist or if the request method is not POST
    # Redirect to admin side view
    return redirect('admin_side')

def pricing(request):
    stripe.api_key = 'sk_test_51P64XRSGntvIRLFwswGIwpRpaoUrDA2f3QHmViSfHcPbMdofy1OUd548fs8nyH9BtMdAKapCDVwsSsvqpw8GLlEL009qoUPJQ3'
    if request.method == 'POST':
        price_id = request.POST.get('price_id')
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            customer_creation='always',
            success_url=settings.REDIRECT_DOMAIN + '/payment_successful?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=settings.REDIRECT_DOMAIN + '/payment_cancelled',
        )
        return redirect(checkout_session.url, code=303)
    return render(request, 'pricing.html')  


## use Stripe dummy card: 4242 4242 4242 4242
def payment_successful(request):
    stripe.api_key = 'sk_test_51P64XRSGntvIRLFwswGIwpRpaoUrDA2f3QHmViSfHcPbMdofy1OUd548fs8nyH9BtMdAKapCDVwsSsvqpw8GLlEL009qoUPJQ3'
    checkout_session_id = request.GET.get('session_id', None)
    session = stripe.checkout.Session.retrieve(checkout_session_id)
    customer = stripe.Customer.retrieve(session.customer)
    price_of_plan = int(str(session.amount_total)[:-2])
    user = User.objects.get(email=request.session['email'])
    current_date = datetime.now().date()
    # Calculate the date after num_days
    if price_of_plan == 500 or price_of_plan == 200:
        num_days = 366
    elif price_of_plan == 25 or price_of_plan == 55:
        num_days = 31
    end_date = current_date + timedelta(days=num_days)
    # Try to get the pricing instance for the user, if it exists
    pricing_instance, created = Pricing.objects.get_or_create(
        user=user,
        defaults={
            'checkout_session_id': checkout_session_id,
            'price_of_plan': price_of_plan,
            'date_of_created': current_date,
            'end_date': end_date,
        }
    )
    # If the pricing instance already existed, update its fields
    if not created:
        pricing_instance.checkout_session_id = checkout_session_id
        pricing_instance.price_of_plan = price_of_plan
        pricing_instance.date_of_created = current_date
        pricing_instance.end_date = end_date
        # You can update other fields here if needed
        pricing_instance.save()

    return render(request, 'payment_successful.html', {'customer': customer})


def payment_cancelled(request):
	stripe.api_key = 'sk_test_51P64XRSGntvIRLFwswGIwpRpaoUrDA2f3QHmViSfHcPbMdofy1OUd548fs8nyH9BtMdAKapCDVwsSsvqpw8GLlEL009qoUPJQ3'
	return render(request, 'payment_cancelled.html')


@csrf_exempt
def stripe_webhook(request):
	stripe.api_key = 'sk_test_51P64XRSGntvIRLFwswGIwpRpaoUrDA2f3QHmViSfHcPbMdofy1OUd548fs8nyH9BtMdAKapCDVwsSsvqpw8GLlEL009qoUPJQ3'
	time.sleep(10)
	payload = request.body
	signature_header = request.META['HTTP_STRIPE_SIGNATURE']
	event = None
	try:
		event = stripe.Webhook.construct_event(
			payload, signature_header, settings.STRIPE_WEBHOOK_SECRET_TEST
		)
	except ValueError as e:
		return HttpResponse(status=400)
	except stripe.error.SignatureVerificationError as e:
		return HttpResponse(status=400)
	if event['type'] == 'checkout.session.completed':
		session = event['data']['object']
		session_id = session.get('id', None)
		time.sleep(15)
		# user_payment = UserPayment.objects.get(stripe_checkout_id=session_id)
		# user_payment.payment_bool = True
		# user_payment.save()
	return HttpResponse(status=200)

