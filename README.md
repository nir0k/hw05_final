# Yatube: A Platform for Publishing Posts

## Choose Your Language

- [English](README.md)
- [Русский](README.ru.md)

---

## General Information

Yatube is a next-generation social network designed for posting and discussing posts. The platform provides users with the ability to share text entries, comment on other users' posts, and follow interesting authors. The comment and subscription systems allow for the creation of a unique community within the platform, where everyone can express themselves and find like-minded individuals.

## Key Features:
1. **Image Handling**

    Utilizes sorl-thumbnail for displaying illustrations for posts on the main page, author's profile page, group page, and individual post page.

2. **Comment System**

    Implemented the ability for users to comment on posts. Only registered users can comment, fostering higher quality and more civilized communication within the community.

3. **Caching**

    Introduced caching for the post list on the main page, which is updated every 20 seconds. This significantly reduces server load and speeds up page loading for the end-user.

4. **Testing**

    Developed tests to check the correctness of image display, the functionality of the comment system, and the efficiency of caching the main page.

### Additional Features:
- **Custom Error Pages**

    Custom error pages for 404 and 403 errors are available, making site navigation more understandable and user-friendly.

- Subscription System

    Implemented a subscription system for authors with the ability to view a feed of posts from favorite users. This feature allows users to keep up with updates from interesting authors and creates conditions for forming friendships and professional connections within the platform.

- Testing New Services

    Conducted testing of the subscription system, including checking the ability to subscribe and unsubscribe, as well as the correct display of posts in the subscription feed.

### Technologies

- Django
- Python
- HTML & CSS

### Project Setup

1. **Clone the repository:**
    ```sh
    git clone git@github.com:nir0k/hw02_community.git
    cd hw02_community
    ```
2. **Create and activate a virtual environment:**
    ```sh
    python3 -m venv env
    source env/bin/activate
    ```
3. **Install dependencies:**
    ```sh
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt
    ```
4. **Apply migrations:**
    ```sh
    cd yatube
    python3 manage.py migrate
    ```
5. **Start the project:**
    ```sh
    python3 manage.py runserver
    ```

### Tests
To run the tests, use the following command:
```sh
python manage.py test
```
This will enable you to check the correctness of the main functions and the platform's stability.