<script lang="ts">
	import Modal from '$lib/components/ui/Modal.svelte';
	import type { UserRole } from '$lib/dtos/AuthDTO';

	let { open, onClose, onInvite }: {
		open: boolean;
		onClose: () => void;
		onInvite: (data: { email: string; name: string; role: UserRole }) => void;
	} = $props();

	let email = $state('');
	let name = $state('');
	let role = $state<UserRole>('viewer');
	let sending = $state(false);

	const emailValido = $derived(/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email));
	const nomeValido = $derived(name.trim().length >= 2);
	const canSubmit = $derived(emailValido && nomeValido && !sending);

	const roles: { value: UserRole; label: string }[] = [
		{ value: 'admin', label: 'Admin' },
		{ value: 'copywriter', label: 'Copywriter' },
		{ value: 'designer', label: 'Designer' },
		{ value: 'reviewer', label: 'Reviewer' },
		{ value: 'viewer', label: 'Viewer' }
	];

	$effect(() => {
		if (open) {
			email = '';
			name = '';
			role = 'viewer';
			sending = false;
		}
	});

	function handleSubmit(e: Event) {
		e.preventDefault();
		if (!canSubmit) return;
		onInvite({ email, name, role });
	}
</script>

<Modal {open} size="md" title="Convidar Usuario" onclose={onClose}>
	<form onsubmit={handleSubmit} class="space-y-4">
		<div>
			<label for="invite-name" class="block text-xs font-medium text-text-secondary mb-1.5">Nome</label>
			<input
				id="invite-name"
				data-testid="campo-nome-convite"
				type="text"
				bind:value={name}
				placeholder="Nome do convidado"
				disabled={sending}
				class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
					focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all
					placeholder:text-text-muted disabled:opacity-50"
			/>
		</div>

		<div>
			<label for="invite-email" class="block text-xs font-medium text-text-secondary mb-1.5">Email</label>
			<input
				id="invite-email"
				data-testid="campo-email-convite"
				type="email"
				bind:value={email}
				placeholder="email@empresa.com"
				disabled={sending}
				class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
					focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all
					placeholder:text-text-muted disabled:opacity-50"
			/>
		</div>

		<div>
			<label for="invite-role" class="block text-xs font-medium text-text-secondary mb-1.5">Perfil</label>
			<select
				id="invite-role"
				data-testid="campo-role-convite"
				bind:value={role}
				disabled={sending}
				class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
					focus:border-purple outline-none cursor-pointer disabled:opacity-50"
			>
				{#each roles as r}
					<option value={r.value}>{r.label}</option>
				{/each}
			</select>
		</div>

		<p class="text-xs text-text-muted">
			O convidado recebera um link para definir sua senha. O link expira em 48 horas.
		</p>
	</form>

	{#snippet footer()}
		<button
			onclick={onClose}
			class="px-4 py-2 rounded-lg text-sm text-text-secondary hover:text-text-primary transition-all cursor-pointer"
		>
			Cancelar
		</button>
		<button
			data-testid="btn-enviar-convite"
			onclick={handleSubmit}
			disabled={!canSubmit}
			class="px-4 py-2 rounded-lg text-sm font-medium text-white bg-purple hover:opacity-90
				transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed
				inline-flex items-center gap-1.5"
		>
			{#if sending}
				<span class="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
				Enviando...
			{:else}
				Enviar Convite
			{/if}
		</button>
	{/snippet}
</Modal>
