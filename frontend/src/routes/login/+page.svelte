<script lang="ts">
	import { goto } from '$app/navigation';
	import { AuthService } from '$lib/services/AuthService';
	import { setAuth, isLoggedIn } from '$lib/stores/auth.svelte';
	import LoginForm from '$lib/components/auth/LoginForm.svelte';
	import SSOButtons from '$lib/components/auth/SSOButtons.svelte';
	import { onMount } from 'svelte';

	let loading = $state(false);
	let error = $state('');

	onMount(() => {
		if (isLoggedIn()) goto('/');
	});

	async function handleLogin(email: string, password: string) {
		loading = true;
		error = '';
		try {
			const result = await AuthService.login(email, password);
			if (result.success && result.data) {
				setAuth(result.data);
				goto('/kanban');
			} else {
				error = result.error ?? 'Email ou senha incorretos.';
			}
		} catch (e) {
			error = 'Erro de conexao com o servidor. Verifique sua internet.';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Login - Content Factory</title>
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

		<LoginForm onSubmit={handleLogin} {loading} {error} />

		<div class="mt-6">
			<SSOButtons disabled={loading} />
		</div>

		<p class="text-center text-[11px] text-text-muted mt-6">
			Acesso restrito. Contate o administrador para obter uma conta.
		</p>
	</div>
</div>
