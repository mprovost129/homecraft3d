from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MessageThread, Message
from .forms import MessageForm
from accounts.models_notification import Notification

@login_required
def inbox(request):
    threads = request.user.message_threads.order_by('-updated_at')
    thread_unread_counts = {}
    for thread in threads:
        thread_unread_counts[thread.id] = thread.messages.filter(is_read=False).exclude(sender=request.user).count()
    return render(request, 'messaging/inbox.html', {
        'threads': threads,
        'thread_unread_counts': thread_unread_counts,
    })

@login_required
def thread_detail(request, thread_id):
    thread = get_object_or_404(MessageThread, id=thread_id, participants=request.user)
    messages = thread.messages.order_by('sent_at')
    # Mark all messages as read for this user
    thread.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.thread = thread
            msg.sender = request.user
            msg.save()
            thread.updated_at = msg.sent_at
            thread.save()
            # Notify other participants
            for user in thread.participants.exclude(id=request.user.id):
                Notification.objects.create(
                    user=user,
                    message=f'New message from {request.user.username}',
                    url=f'/messaging/thread/{thread.id}/'
                )
            return redirect('messaging:thread_detail', thread_id=thread.id)
    else:
        form = MessageForm()
    return render(request, 'messaging/thread_detail.html', {'thread': thread, 'messages': messages, 'form': form})

@login_required
def start_thread(request, user_id):
    from accounts.models import User
    other_user = get_object_or_404(User, id=user_id)
    # Check if a thread already exists
    thread = MessageThread.objects.filter(participants=request.user).filter(participants=other_user).first()
    if not thread:
        thread = MessageThread.objects.create()
        thread.participants.add(request.user, other_user)
    return redirect('messaging:thread_detail', thread_id=thread.id)
