<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { getToastStore } from '@skeletonlabs/skeleton-svelte';

	const dispatch = createEventDispatcher<{
		filesSelected: File[];
	}>();

	const toastStore = getToastStore();

	let fileInput: HTMLInputElement;
	let dragOver = false;

	// Supported file types
	const supportedTypes = [
		'application/pdf',
		'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
		'application/msword',
		'text/plain',
		'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
		'application/vnd.ms-excel',
		'text/csv'
	];

	const maxFileSize = 10 * 1024 * 1024; // 10MB

	function handleFileSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		if (target.files) {
			processFiles(Array.from(target.files));
		}
	}

	function handleDrop(event: DragEvent) {
		event.preventDefault();
		dragOver = false;

		if (event.dataTransfer?.files) {
			processFiles(Array.from(event.dataTransfer.files));
		}
	}

	function handleDragOver(event: DragEvent) {
		event.preventDefault();
		dragOver = true;
	}

	function handleDragLeave(event: DragEvent) {
		event.preventDefault();
		dragOver = false;
	}

	function processFiles(files: File[]) {
		const validFiles: File[] = [];
		const errors: string[] = [];

		files.forEach(file => {
			// Check file type
			if (!supportedTypes.includes(file.type)) {
				errors.push(`${file.name}: Unsupported file type`);
				return;
			}

			// Check file size
			if (file.size > maxFileSize) {
				errors.push(`${file.name}: File too large (max 10MB)`);
				return;
			}

			validFiles.push(file);
		});

		if (errors.length > 0) {
			toastStore.trigger({
				message: `File upload errors:\n${errors.join('\n')}`,
				background: 'variant-filled-error'
			});
		}

		if (validFiles.length > 0) {
			dispatch('filesSelected', validFiles);
			
			// Reset file input
			if (fileInput) {
				fileInput.value = '';
			}
		}
	}

	function openFileDialog() {
		fileInput?.click();
	}
</script>

<!-- Hidden file input -->
<input
	bind:this={fileInput}
	type="file"
	multiple
	accept=".pdf,.docx,.doc,.txt,.xlsx,.xls,.csv"
	onchange={handleFileSelect}
	class="hidden"
/>

<!-- Upload button with drag and drop -->
<div class="relative">
	<button
		class="btn variant-ghost-surface"
		onclick={openFileDialog}
		ondrop={handleDrop}
		ondragover={handleDragOver}
		ondragleave={handleDragLeave}
		title="Upload files (PDF, Word, Excel, CSV, TXT)"
		class:variant-filled-primary={dragOver}
	>
		<i class="fa-solid fa-paperclip"></i>
	</button>

	<!-- Drag overlay -->
	{#if dragOver}
		<div class="absolute inset-0 bg-primary-500 bg-opacity-20 rounded-lg border-2 border-dashed border-primary-500 flex items-center justify-center">
			<span class="text-xs text-primary-600 font-medium">Drop files here</span>
		</div>
	{/if}
</div>

<!-- File type info tooltip -->
<div class="hidden group-hover:block absolute bottom-full left-0 mb-2 p-2 bg-surface-900 text-white text-xs rounded shadow-lg whitespace-nowrap z-10">
	Supported: PDF, Word, Excel, CSV, TXT (max 10MB each)
</div>
