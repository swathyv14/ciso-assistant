<script lang="ts">
	import { onMount, createEventDispatcher, tick } from 'svelte';
	import { BASE_API_URL } from '$lib/utils/constants';
	import { getToastStore } from '@skeletonlabs/skeleton-svelte';
	import ChatMessage from './ChatMessage.svelte';
	import FileUpload from './FileUpload.svelte';

	export let session: any;

	const dispatch = createEventDispatcher();
	const toastStore = getToastStore();

	let messages: any[] = [];
	let newMessage = '';
	let loading = false;
	let messagesContainer: HTMLElement;
	let uploadedFiles: File[] = [];

	onMount(async () => {
		await loadMessages();
	});

	$: if (session) {
		loadMessages();
	}

	async function loadMessages() {
		if (!session) return;

		try {
			const response = await fetch(
				`${BASE_API_URL}/chatbot/messages/?session_id=${session.id}`,
				{
					credentials: 'include'
				}
			);

			if (response.ok) {
				const data = await response.json();
				messages = data.results || data;
				await tick();
				scrollToBottom();
			}
		} catch (error) {
			console.error('Error loading messages:', error);
		}
	}

	async function sendMessage() {
		if (!newMessage.trim() && uploadedFiles.length === 0) return;
		if (loading) return;

		const messageText = newMessage.trim();
		newMessage = '';
		loading = true;

		// Add user message to UI immediately
		if (messageText) {
			messages = [
				...messages,
				{
					id: Date.now(),
					role: 'user',
					content: messageText,
					created_at: new Date().toISOString()
				}
			];
		}

		await tick();
		scrollToBottom();

		try {
			const formData = new FormData();
			formData.append('message', messageText || 'Please analyze the uploaded files.');
			formData.append('session_id', session.id);

			// Add uploaded files
			uploadedFiles.forEach((file, index) => {
				formData.append(`files`, file);
			});

			const response = await fetch(`${BASE_API_URL}/chatbot/bot/chat/`, {
				method: 'POST',
				credentials: 'include',
				body: formData
			});

			if (response.ok) {
				const data = await response.json();
				
				// Update messages with the actual user message and assistant response
				messages = messages.filter(m => m.id !== Date.now()); // Remove temporary message
				messages = [
					...messages,
					data.user_message,
					data.assistant_response
				];

				// Clear uploaded files
				uploadedFiles = [];

				// Dispatch event to update session list
				dispatch('sessionUpdated');

				await tick();
				scrollToBottom();
			} else {
				const errorData = await response.json();
				toastStore.trigger({
					message: errorData.error || 'Failed to send message',
					background: 'variant-filled-error'
				});
				
				// Remove the temporary user message on error
				messages = messages.filter(m => m.id !== Date.now());
			}
		} catch (error) {
			console.error('Error sending message:', error);
			toastStore.trigger({
				message: 'Error sending message',
				background: 'variant-filled-error'
			});
			
			// Remove the temporary user message on error
			messages = messages.filter(m => m.id !== Date.now());
		} finally {
			loading = false;
		}
	}

	function scrollToBottom() {
		if (messagesContainer) {
			messagesContainer.scrollTop = messagesContainer.scrollHeight;
		}
	}

	function handleKeyPress(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			sendMessage();
		}
	}

	function handleFilesSelected(event: CustomEvent<File[]>) {
		uploadedFiles = [...uploadedFiles, ...event.detail];
	}

	function removeFile(index: number) {
		uploadedFiles = uploadedFiles.filter((_, i) => i !== index);
	}
</script>

<div class="flex flex-col h-full">
	<!-- Header -->
	<div class="p-4 border-b border-surface-300-600-token bg-surface-100-800-token">
		<div class="flex items-center justify-between">
			<div>
				<h2 class="font-semibold">{session.title || 'Chat Session'}</h2>
				<p class="text-sm text-surface-600-300-token">
					{messages.length} messages
				</p>
			</div>
			<div class="flex items-center space-x-2">
				<span class="text-xs text-surface-500-400-token">
					{new Date(session.created_at).toLocaleDateString()}
				</span>
			</div>
		</div>
	</div>

	<!-- Messages -->
	<div
		bind:this={messagesContainer}
		class="flex-1 overflow-y-auto p-4 space-y-4 bg-surface-50-900-token"
	>
		{#if messages.length === 0}
			<div class="text-center text-surface-600-300-token py-8">
				<i class="fa-solid fa-comments text-3xl mb-4"></i>
				<p>Start a conversation with the AI assistant!</p>
				<p class="text-sm mt-2">
					Ask questions about CISO Assistant, upload documents, or get cybersecurity guidance.
				</p>
			</div>
		{:else}
			{#each messages as message}
				<ChatMessage {message} />
			{/each}
		{/if}

		{#if loading}
			<div class="flex items-start space-x-3">
				<div class="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
					<i class="fa-solid fa-robot text-white text-sm"></i>
				</div>
				<div class="flex-1 bg-surface-200-700-token rounded-lg p-3">
					<div class="flex items-center space-x-2">
						<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-500"></div>
						<span class="text-sm text-surface-600-300-token">AI is thinking...</span>
					</div>
				</div>
			</div>
		{/if}
	</div>

	<!-- Input area -->
	<div class="p-4 border-t border-surface-300-600-token bg-surface-100-800-token">
		<!-- File upload area -->
		{#if uploadedFiles.length > 0}
			<div class="mb-3 p-3 bg-surface-200-700-token rounded-lg">
				<div class="flex items-center justify-between mb-2">
					<span class="text-sm font-medium">Uploaded Files:</span>
					<button
						class="btn btn-sm variant-ghost-error"
						onclick={() => (uploadedFiles = [])}
					>
						Clear All
					</button>
				</div>
				<div class="space-y-2">
					{#each uploadedFiles as file, index}
						<div class="flex items-center justify-between p-2 bg-surface-300-600-token rounded">
							<div class="flex items-center space-x-2">
								<i class="fa-solid fa-file text-primary-500"></i>
								<span class="text-sm">{file.name}</span>
								<span class="text-xs text-surface-500-400-token">
									({(file.size / 1024).toFixed(1)} KB)
								</span>
							</div>
							<button
								class="btn btn-sm variant-ghost-error"
								onclick={() => removeFile(index)}
							>
								<i class="fa-solid fa-times"></i>
							</button>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<div class="flex items-end space-x-2">
			<FileUpload on:filesSelected={handleFilesSelected} />
			
			<div class="flex-1">
				<textarea
					bind:value={newMessage}
					onkeypress={handleKeyPress}
					placeholder="Ask me anything about CISO Assistant or cybersecurity..."
					class="textarea w-full resize-none"
					rows="1"
					disabled={loading}
				></textarea>
			</div>
			
			<button
				class="btn variant-filled-primary"
				onclick={sendMessage}
				disabled={loading || (!newMessage.trim() && uploadedFiles.length === 0)}
			>
				{#if loading}
					<i class="fa-solid fa-spinner animate-spin"></i>
				{:else}
					<i class="fa-solid fa-paper-plane"></i>
				{/if}
			</button>
		</div>
		
		<div class="text-xs text-surface-500-400-token mt-2 text-center">
			Press Enter to send, Shift+Enter for new line
		</div>
	</div>
</div>
