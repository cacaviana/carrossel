<script lang="ts">
	import Modal from '$lib/components/ui/Modal.svelte';
	import type { UserDTO } from '$lib/dtos/UserDTO';
	import type { UserRole } from '$lib/dtos/AuthDTO';

	let { open, user = null, onClose, onSave }: {
		open: boolean;
		user: UserDTO | null;
		onClose: () => void;
		onSave: (data: Record<string, any>) => void;
	} = $props();

	let name = $state('');
	let email = $state('');
	let password = $state('');
	let role = $state<UserRole>('viewer');
	let saving = $state(false);
	let error = $state('');

	const isEdit = $derived(user !== null);
	const title = $derived(isEdit ? 'Editar Usuario' : 'Criar Usuario');

	const emailValido = $derived(/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email));
	const nomeValido = $derived(name.trim().length >= 2);
	const senhaForte = $derived(
		password.length >= 8 &&
		/[A-Z]/.test(password) &&
		/[0-9]/.test(password) &&
		/[^A-Za-z0-9]/.test(password)
	);
	const canSubmit = $derived(
		nomeValido && emailValido && (isEdit || senhaForte) && !saving
	);

	const roles: { value: UserRole; label: string }[] = [
		{ value: 'admin', label: 'Admin' },
		{ value: 'copywriter', label: 'Copywriter' },
		{ value: 'designer', label: 'Designer' },
		{ value: 'reviewer', label: 'Reviewer' },
		{ value: 'viewer', label: 'Viewer' }
	];

	$effect(() => {
		if (open && user) {
			name = user.name;
			email = user.email;
			role = user.role;
			password = '';
			error = '';
		} else if (open) {
			name = '';
			email = '';
			role = 'viewer';
			password = '';
			error = '';
		}
	});

	async function handleSubmit(e: Event) {
		e.preventDefault();
		if (!canSubmit) return;

		saving = true;
		error = '';
		try {
			if (isEdit) {
				onSave({ user_id: user!.id, name, role });
			} else {
				onSave({ name, email, password, role });
			}
		} catch (err: any) {
			error = err.message ?? 'Erro ao salvar';
		} finally {
			saving = false;
		}
	}
</script>

<Modal {open} size="md" {title} onclose={onClose}>
	<form onsubmit={handleSubmit} class="space-y-4">
		<div>
			<label for="user-name" class="block text-xs font-medium text-text-secondary mb-1.5">Nome</label>
			<input
				id="user-name"
				data-testid="campo-nome-usuario"
				type="text"
				bind:value={name}
				placeholder="Nome completo"
				disabled={saving}
				class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
					focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all
					placeholder:text-text-muted disabled:opacity-50"
			/>
			{#if name.length > 0 && !nomeValido}
				<p class="text-[11px] text-red mt-1">Minimo 2 caracteres</p>
			{/if}
		</div>

		<div>
			<label for="user-email" class="block text-xs font-medium text-text-secondary mb-1.5">Email</label>
			<input
				id="user-email"
				data-testid="campo-email-usuario"
				type="email"
				bind:value={email}
				placeholder="usuario@email.com"
				disabled={saving || isEdit}
				class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
					focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all
					placeholder:text-text-muted disabled:opacity-50"
			/>
		</div>

		{#if !isEdit}
			<div>
				<label for="user-password" class="block text-xs font-medium text-text-secondary mb-1.5">Senha</label>
				<input
					id="user-password"
					data-testid="campo-senha-usuario"
					type="password"
					bind:value={password}
					placeholder="Senha forte"
					disabled={saving}
					class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
						focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all
						placeholder:text-text-muted disabled:opacity-50"
				/>
				{#if password.length > 0 && !senhaForte}
					<p class="text-[11px] text-text-muted mt-1">Min 8 chars, 1 maiuscula, 1 numero, 1 especial</p>
				{/if}
			</div>
		{/if}

		<div>
			<label for="user-role" class="block text-xs font-medium text-text-secondary mb-1.5">Perfil</label>
			<select
				id="user-role"
				data-testid="campo-role-usuario"
				bind:value={role}
				disabled={saving}
				class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
					focus:border-purple outline-none cursor-pointer disabled:opacity-50"
			>
				{#each roles as r}
					<option value={r.value}>{r.label}</option>
				{/each}
			</select>
		</div>

		{#if error}
			<div data-testid="msg-erro" class="p-3 rounded-lg bg-red/10 border border-red/20 text-sm text-red">
				{error}
			</div>
		{/if}
	</form>

	{#snippet footer()}
		<button
			onclick={onClose}
			class="px-4 py-2 rounded-lg text-sm text-text-secondary hover:text-text-primary transition-all cursor-pointer"
		>
			Cancelar
		</button>
		<button
			data-testid="btn-salvar-usuario"
			onclick={handleSubmit}
			disabled={!canSubmit}
			class="px-4 py-2 rounded-lg text-sm font-medium text-white bg-purple hover:opacity-90
				transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed
				inline-flex items-center gap-1.5"
		>
			{#if saving}
				<span class="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
				Salvando...
			{:else}
				{isEdit ? 'Salvar' : 'Criar'}
			{/if}
		</button>
	{/snippet}
</Modal>
