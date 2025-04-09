from flask import render_template, redirect, url_for, flash, request, session, jsonify
from form import RegisterForm, LoginForm
from modeule import User, ChatHistory, db, app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from langchain_core.runnables import RunnableConfig
import os
import sys

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

from Main_agent import compile_main_agent_graph

agent = compile_main_agent_graph()

@app.route('/')
@app.route('/login_page', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            session['chat_session'] = []
            return redirect(url_for('chat_page'))
        else:
            flash('Username and Password do not match! Please try again.', category='danger')
    return render_template('login.html', form=form)

@app.route('/register_page', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(
            username=form.username.data,
            email=form.email_address.data,
            password=form.password1.data
        )
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Account created successfully! You are now logged in as: {user_to_create.username}', category='success')
        session['chat_session'] = []
        return redirect(url_for('chat_page'))

    elif form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)


def save_to_history(sender, message):
    if 'chat_session' not in session:
        session['chat_session'] = []
    session['chat_session'].append({
        'sender': sender,
        'message': message,
        'timestamp': str(datetime.utcnow())
    })
    session.modified = True

def get_bot_response(user_message,user_id):
    test_input = {
    "messages_query": user_message
    }
    config = RunnableConfig(
        configurable={"user_id": user_id}
    )
    response = agent.invoke(test_input,config = config)
    return response["generated_email"]

@app.route('/chatbot', methods=['POST'])
@login_required
def chatbot():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message received'}), 400

    save_to_history('user', user_message)

    bot_response = get_bot_response(user_message, current_user.id)
    save_to_history('bot', bot_response)

    return jsonify({'response': bot_response})


@app.route('/logout')
@login_required
def logout():
    if 'chat_session' in session and session['chat_session']:
        conversation_text = '\n'.join([f"{msg['sender']}: {msg['message']}" for msg in session['chat_session']])
        title = f"Chat on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        new_history = ChatHistory(
            user_id=current_user.id,
            title=title,
            conversation=conversation_text
        )
        db.session.add(new_history)
        db.session.commit()
    session.pop('chat_session', None)
    logout_user()
    flash("You have been logged out and your chat has been saved.", category="info")
    return redirect(url_for('login_page'))

@app.route('/chat_history')
@login_required
def chat_history():
    histories = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.desc()).all()
    return render_template('chat_history.html', histories=histories)

@app.route('/chat_history/<int:history_id>')
@login_required
def view_chat(history_id):
    history = ChatHistory.query.get_or_404(history_id)
    if history.user_id != current_user.id:
        flash("You are not authorized to view this chat.", category='danger')
        return redirect(url_for('chat_history'))
    return render_template('chat_detail.html', chat=history)

@app.route('/chat_page')
@login_required
def chat_page():
    histories = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.desc()).all()
    return render_template('chat.html', histories=histories)


if __name__ == '__main__':
    app.run(debug=True)
