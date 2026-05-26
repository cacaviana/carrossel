<script lang="ts">
	import { LoginRequestDTO } from '$lib/dtos/LoginRequestDTO';

	let { onSubmit, loading = false, error = '' }: {
		onSubmit: (email: string, password: string) => void;
		loading: boolean;
		error: string;
	} = $props();

	let email = $state('');
	let password = $state('');
	let showPassword = $state(false);
	let touched = $state(false);

	const dto = $derived(new LoginRequestDTO({ email, password }));
	const errosSenha = $derived(touched && password.length > 0 ? dto.errosSenha : []);
	const canSubmit = $derived(dto.isValid() && !loading);

	function handleSubmit(e: Event) {
		e.preventDefault();
		touched = true;
		if (canSubmit) {
			onSubmit(email, password);
		}
	}
</script>

<form onsubmit={handleSubmit} class="space-y-4">
	<div>
		<label for="email" class="block text-xs font-medium text-text-secondary mb-1.5">Email</label>
		<input
			id="email"
			data-testid="campo-email"
			type="email"
			bind:value={email}
			placeholder="seu@email.com"
			disabled={loading}
			class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
				focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all
				placeholder:text-text-muted disabled:opacity-50"
		/>
	</div>

	<div>
		<label for="password" class="block text-xs font-medium text-text-secondary mb-1.5">Senha</label>
		<div class="relative">
			<input
				id="password"
				data-testid="campo-senha"
				type={showPassword ? 'text' : 'password'}
				bind:value={password}
				placeholder="Sua senha"
				disabled={loading}
				onfocus={() => touched = true}
				class="w-full px-4 py-2.5 pr-10 rounded-lg border text-text-primary text-sm
					focus:ring-3 outline-none transition-all
					placeholder:text-text-muted disabled:opacity-50
					{errosSenha.length > 0 ? 'border-red ring-red/12' : 'border-border-default bg-bg-input focus:border-purple focus:ring-purple/12'}"
			/>
			<button
				type="button"
				onclick={() => showPassword = !showPassword}
				class="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary transition-colors cursor-pointer"
				tabindex={-1}
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					{#if showPassword}
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
					{:else}
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
					{/if}
				</svg>
			</button>
		</div>

		{#if errosSenha.length > 0}
			<div class="mt-2 space-y-1">
				{#each errosSenha as e}
					<p class="text-[11px] text-red flex items-center gap-1">
						<svg class="w-3 h-3 shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>
						{e}
					</p>
				{/each}
			</div>
		{/if}
	</div>

	{#if error}
		<div data-testid="msg-erro" class="p-3 rounded-lg bg-red/10 border border-red/20 text-sm text-red animate-fade-up">
			{error}
		</div>
	{/if}

	<button
		data-testid="btn-entrar"
		type="submit"
		disabled={!canSubmit}
		class="w-full py-3 rounded-lg font-medium text-sm text-white transition-all cursor-pointer
			bg-purple hover:shadow-[0_0_30px_rgba(53,120,176,0.25)] hover:opacity-90
			disabled:opacity-50 disabled:cursor-not-allowed"
	>
		{#if loading}
			<span class="inline-flex items-center gap-2">
				<span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
				Entrando...
			</span>
		{:else}
			Entrar
		{/if}
	</button>
</form>
