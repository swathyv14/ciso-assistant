<script lang="ts">
	import { getToastStore } from '@skeletonlabs/skeleton-svelte';

	export let message: any;

	const toastStore = getToastStore();

	function copyToClipboard(text: string) {
		navigator.clipboard.writeText(text).then(() => {
			toastStore.trigger({
				message: 'Message copied to clipboard',
				background: 'variant-filled-success'
			});
		});
	}

	function formatTimestamp(timestamp: string) {
		const date = new Date(timestamp);
		return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
	}

	// Simple markdown-like formatting
	function formatContent(content: string) {
		return content
			.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
			.replace(/\*(.*?)\*/g, '<em>$1</em>')
			.replace(/`(.*?)`/g, '<code class="bg-surface-300-600-token px-1 rounded">$1</code>')
			.replace(/\n/g, '<br>');
	}
</script>

<div class="flex items-start space-x-3 {message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}">
	<!-- Avatar -->
	<div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 {
		message.role === 'user' 
			? 'bg-primary-500' 
			: message.role === 'assistant' 
				? 'bg-secondary-500' 
				: 'bg-surface-500'
	}">
		{#if message.role === 'user'}
			<i class="fa-solid fa-user text-white text-sm"></i>
		{:else if message.role === 'assistant'}
			<i class="fa-solid fa-robot text-white text-sm"></i>
		{:else}
			<i class="fa-solid fa-cog text-white text-sm"></i>
		{/if}
	</div>

	<!-- Message content -->
	<div class="flex-1 max-w-4xl">
		<div class="rounded-lg p-3 {
			message.role === 'user' 
				? 'bg-primary-500 text-white ml-auto max-w-md' 
				: 'bg-surface-200-700-token'
		}">
			<!-- Message text -->
			<div class="prose prose-sm max-w-none {message.role === 'user' ? 'prose-invert' : ''}">
				{@html formatContent(message.content)}
			</div>

			<!-- Metadata -->
			{#if message.metadata && Object.keys(message.metadata).length > 0}
				<div class="mt-2 pt-2 border-t border-surface-300-600-token">
					{#if message.metadata.files_processed}
						<div class="text-xs opacity-75">
							<i class="fa-solid fa-file mr-1"></i>
							{message.metadata.files_processed} file(s) processed
						</div>
					{/if}
				</div>
			{/if}
		</div>

		<!-- Message footer -->
		<div class="flex items-center justify-between mt-1 px-1">
			<span class="text-xs text-surface-500-400-token">
				{formatTimestamp(message.created_at)}
			</span>
			
			<div class="flex items-center space-x-1">
				<!-- Copy button -->
				<button
					class="btn btn-sm variant-ghost-surface opacity-50 hover:opacity-100"
					onclick={() => copyToClipboard(message.content)}
					title="Copy message"
				>
					<i class="fa-solid fa-copy text-xs"></i>
				</button>

				<!-- Role indicator -->
				<span class="text-xs px-2 py-1 rounded-full {
					message.role === 'user' 
						? 'bg-primary-100-800-token text-primary-600-300-token' 
						: message.role === 'assistant'
							? 'bg-secondary-100-800-token text-secondary-600-300-token'
							: 'bg-surface-300-600-token'
				}">
					{message.role === 'user' ? 'You' : message.role === 'assistant' ? 'AI' : 'System'}
				</span>
			</div>
		</div>
	</div>
</div>

<style>
	:global(.prose code) {
		@apply bg-surface-300-600-token px-1 py-0.5 rounded text-sm;
	}
	
	:global(.prose pre) {
		@apply bg-surface-300-600-token p-3 rounded-lg overflow-x-auto;
	}
	
	:global(.prose pre code) {
		@apply bg-transparent p-0;
	}
	
	:global(.prose-invert code) {
		@apply bg-primary-600 bg-opacity-50;
	}
	
	:global(.prose-invert pre) {
		@apply bg-primary-600 bg-opacity-50;
	}
</style>
