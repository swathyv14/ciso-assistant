<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { pageTitle } from '$lib/utils/stores';
	import { BASE_API_URL } from '$lib/utils/constants';
	import { getToastStore } from '@skeletonlabs/skeleton-svelte';
	import ChatInterface from '$lib/components/Chatbot/ChatInterface.svelte';
	import { m } from '$paraglide/messages';

	const toastStore = getToastStore();

	// Set page title
	pageTitle.set('AI Assistant');

	let chatSessions: any[] = [];
	let currentSession: any = null;
	let loading = false;

	onMount(async () => {
		await loadChatSessions();
	});

	async function loadChatSessions() {
		try {
			loading = true;
			const response = await fetch(`${BASE_API_URL}/chatbot/sessions/`, {
				credentials: 'include'
			});

			if (response.ok) {
				const data = await response.json();
				chatSessions = data.results || data;
			} else {
				console.error('Failed to load chat sessions');
			}
		} catch (error) {
			console.error('Error loading chat sessions:', error);
		} finally {
			loading = false;
		}
	}

	async function createNewSession() {
		try {
			const response = await fetch(`${BASE_API_URL}/chatbot/sessions/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				credentials: 'include',
				body: JSON.stringify({
					title: 'New Chat'
				})
			});

			if (response.ok) {
				const newSession = await response.json();
				chatSessions = [newSession, ...chatSessions];
				currentSession = newSession;
			} else {
				toastStore.trigger({
					message: 'Failed to create new chat session',
					background: 'variant-filled-error'
				});
			}
		} catch (error) {
			console.error('Error creating new session:', error);
			toastStore.trigger({
				message: 'Error creating new chat session',
				background: 'variant-filled-error'
			});
		}
	}

	function selectSession(session: any) {
		currentSession = session;
	}

	async function deleteSession(sessionId: string) {
		try {
			const response = await fetch(`${BASE_API_URL}/chatbot/sessions/${sessionId}/`, {
				method: 'DELETE',
				credentials: 'include'
			});

			if (response.ok) {
				chatSessions = chatSessions.filter(s => s.id !== sessionId);
				if (currentSession?.id === sessionId) {
					currentSession = null;
				}
				toastStore.trigger({
					message: 'Chat session deleted',
					background: 'variant-filled-success'
				});
			}
		} catch (error) {
			console.error('Error deleting session:', error);
		}
	}
</script>

<div class="flex h-full max-h-screen">
	<!-- Sidebar with chat sessions -->
	<div class="w-80 bg-surface-100-800-token border-r border-surface-300-600-token flex flex-col">
		<!-- Header -->
		<div class="p-4 border-b border-surface-300-600-token">
			<div class="flex items-center justify-between mb-4">
				<h2 class="text-lg font-semibold">
					<i class="fa-solid fa-robot mr-2"></i>
					AI Assistant
				</h2>
				<button
					class="btn btn-sm variant-filled-primary"
					onclick={createNewSession}
					disabled={loading}
				>
					<i class="fa-solid fa-plus mr-1"></i>
					New Chat
				</button>
			</div>
			<p class="text-sm text-surface-600-300-token">
				Ask questions about CISO Assistant, cybersecurity, and get help with your GRC tasks.
			</p>
		</div>

		<!-- Chat sessions list -->
		<div class="flex-1 overflow-y-auto p-2">
			{#if loading}
				<div class="flex justify-center p-4">
					<div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-500"></div>
				</div>
			{:else if chatSessions.length === 0}
				<div class="text-center p-4 text-surface-600-300-token">
					<i class="fa-solid fa-comments text-2xl mb-2"></i>
					<p>No chat sessions yet</p>
					<p class="text-xs">Start a new conversation!</p>
				</div>
			{:else}
				{#each chatSessions as session}
					<div
						class="p-3 mb-2 rounded-lg cursor-pointer transition-colors hover:bg-surface-200-700-token {currentSession?.id === session.id ? 'bg-primary-100-800-token border border-primary-500' : 'bg-surface-50-900-token'}"
						onclick={() => selectSession(session)}
					>
						<div class="flex items-start justify-between">
							<div class="flex-1 min-w-0">
								<h3 class="font-medium text-sm truncate">
									{session.title || 'New Chat'}
								</h3>
								<p class="text-xs text-surface-600-300-token mt-1">
									{session.message_count} messages
								</p>
								{#if session.last_message}
									<p class="text-xs text-surface-500-400-token mt-1 truncate">
										{session.last_message.content}
									</p>
								{/if}
							</div>
							<button
								class="btn btn-sm variant-ghost-error ml-2"
								onclick={(e) => {
									e.stopPropagation();
									deleteSession(session.id);
								}}
							>
								<i class="fa-solid fa-trash text-xs"></i>
							</button>
						</div>
						<div class="text-xs text-surface-500-400-token mt-2">
							{new Date(session.created_at).toLocaleDateString()}
						</div>
					</div>
				{/each}
			{/if}
		</div>
	</div>

	<!-- Main chat area -->
	<div class="flex-1 flex flex-col">
		{#if currentSession}
			<ChatInterface session={currentSession} on:sessionUpdated={loadChatSessions} />
		{:else}
			<!-- Welcome screen -->
			<div class="flex-1 flex items-center justify-center bg-surface-50-900-token">
				<div class="text-center max-w-md">
					<div class="text-6xl mb-6">
						<i class="fa-solid fa-robot text-primary-500"></i>
					</div>
					<h1 class="text-2xl font-bold mb-4">Welcome to CISO Assistant AI</h1>
					<p class="text-surface-600-300-token mb-6">
						I'm here to help you with cybersecurity questions, navigate CISO Assistant features, 
						and assist with your governance, risk, and compliance tasks.
					</p>
					<div class="grid grid-cols-1 gap-3 text-left">
						<div class="p-3 bg-surface-100-800-token rounded-lg">
							<h3 class="font-semibold text-sm mb-1">
								<i class="fa-solid fa-question-circle mr-2 text-primary-500"></i>
								Ask Questions
							</h3>
							<p class="text-xs text-surface-600-300-token">
								Get help with CISO Assistant features and cybersecurity concepts
							</p>
						</div>
						<div class="p-3 bg-surface-100-800-token rounded-lg">
							<h3 class="font-semibold text-sm mb-1">
								<i class="fa-solid fa-upload mr-2 text-primary-500"></i>
								Upload Documents
							</h3>
							<p class="text-xs text-surface-600-300-token">
								Upload files for analysis and get insights
							</p>
						</div>
						<div class="p-3 bg-surface-100-800-token rounded-lg">
							<h3 class="font-semibold text-sm mb-1">
								<i class="fa-solid fa-database mr-2 text-primary-500"></i>
								Access Data
							</h3>
							<p class="text-xs text-surface-600-300-token">
								Get information about your frameworks, risks, and assessments
							</p>
						</div>
					</div>
					<button
						class="btn variant-filled-primary mt-6"
						onclick={createNewSession}
					>
						<i class="fa-solid fa-plus mr-2"></i>
						Start New Conversation
					</button>
				</div>
			</div>
		{/if}
	</div>
</div>
