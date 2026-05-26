<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { AuthService } from '$lib/services/AuthService';
	import { setAuth } from '$lib/stores/auth.svelte';
	import { LoginRequestDTO } from '$lib/dtos/LoginRequestDTO';

	let password = $state('');
	let confirmPassword = $state('');
	let loading = $state(false);
	let error = $state('');
	let showPassword = $state(false);
	let touched = $state(false);

	const token = $derived(page.url.searchParams.get('token') ?? '');
	const hasToken = $derived(token.length > 0);

	const dto = $derived(new LoginRequestDTO({ email: 'invite@placeholder.com', password }));
	const errosSenha = $derived(touched && password.length > 0 ? dto.errosSenha : []);
	const senhasIguais = $derived(password === confirmPassword);
	const canSubmit = $derived(
		hasToken && dto.senhaForte && senhasIguais && !loading
	);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		touched = true;
		if (!canSubmit) return;

		loading = true;
		error = '';
		try {
			const authData = await AuthService.aceitarConvite(token, password);
			setAuth(authData);
			goto('/historico');
		} catch (err: any) {
			error = err.message ?? 'Erro ao aceitar convite.';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Aceitar Convite - Content Factory</title>
</svelte:head>

<div class="hero-bg min-h-screen flex items-center justify-center px-4">
	<div class="w-full max-w-md bg-bg-card rounded-2xl border border-border-default shadow-lg p-8 animate-fade-up">
		<!-- Logo -->
		<div class="flex items-center gap-3 mb-8">
			<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-steel-3 to-steel-5 flex items-center justify-center text-white font-bold text-sm shadow-sm">
				CF
			</div>
			<div>
				<p class="text-base font-semibold text-text-primary tracking-tight">Content Factory</p>
				<p class="text-[11px] text-text-muted">IT Valley School</p>
			</div>
		</div>

		{#if !hasToken}
			<div class="text-center py-8">
				<p class="text-text-secondary text-sm">Link de convite invalido ou ausente.</p>
				<a href="/login" class="text-sm text-purple hover:underline mt-3 inline-block">Ir para login</a>
			</div>
		{:else}
			<h2 class="text-lg font-semibold text-text-primary mb-2">Defina sua senha</h2>
			<p class="text-sm text-text-muted mb-6">Crie uma senha para acessar o Content Factory.</p>

			<form onsubmit={handleSubmit} class="space-y-4">
				<div>
					<label for="new-password" class="block text-xs font-medium text-text-secondary mb-1.5">Senha</label>
					<div class="relative">
						<input
							id="new-password"
							data-testid="campo-senha-convite"
							type={showPassword ? 'text' : 'password'}
							bind:value={password}
							placeholder="Senha forte"
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

				<div>
					<label for="confirm-password" class="block text-xs font-medium text-text-secondary mb-1.5">Confirmar Senha</label>
					<input
						id="confirm-password"
						data-testid="campo-confirmar-senha-convite"
						type="password"
						bind:value={confirmPassword}
						placeholder="Repita a senha"
						disabled={loading}
						class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
							focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all
							placeholder:text-text-muted disabled:opacity-50"
					/>
					{#if confirmPassword.length > 0 && !senhasIguais}
						<p class="text-[11px] text-red mt-1">As senhas nao coincidem</p>
					{/if}
				</div>

				{#if error}
					<div data-testid="msg-erro" class="p-3 rounded-lg bg-red/10 border border-red/20 text-sm text-red animate-fade-up">
						{error}
					</div>
				{/if}

				<button
					data-testid="btn-aceitar-convite"
					type="submit"
					disabled={!canSubmit}
					class="w-full py-3 rounded-lg font-medium text-sm text-white transition-all cursor-pointer
						bg-purple hover:shadow-[0_0_30px_rgba(53,120,176,0.25)] hover:opacity-90
						disabled:opacity-50 disabled:cursor-not-allowed"
				>
					{#if loading}
						<span class="inline-flex items-center gap-2">
							<span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
							Criando conta...
						</span>
					{:else}
						Criar Conta
					{/if}
				</button>
			</form>
		{/if}
	</div>
</div>
