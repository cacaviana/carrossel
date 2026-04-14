<script lang="ts">
	import type { UserDTO } from '$lib/dtos/UserDTO';

	let { users, onEdit, onToggleStatus, onInvite }: {
		users: UserDTO[];
		onEdit: (user: UserDTO) => void;
		onToggleStatus: (user: UserDTO) => void;
		onInvite: () => void;
	} = $props();
</script>

<div class="space-y-4">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h2 class="text-lg font-semibold text-text-primary">Usuarios</h2>
			<p class="text-sm text-text-muted">{users.length} usuario{users.length !== 1 ? 's' : ''}</p>
		</div>
		<button
			data-testid="btn-convidar"
			onclick={onInvite}
			class="px-4 py-2 rounded-lg font-medium text-sm text-white
				bg-purple hover:opacity-90 transition-all cursor-pointer
				inline-flex items-center gap-1.5"
		>
			<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
			</svg>
			Convidar
		</button>
	</div>

	<!-- Table -->
	<div class="bg-bg-card rounded-xl border border-border-default overflow-hidden">
		<div class="overflow-x-auto">
			<table class="w-full text-sm" data-testid="tabela-usuarios">
				<thead>
					<tr class="border-b border-border-default bg-bg-elevated/50">
						<th class="text-left px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider">Usuario</th>
						<th class="text-left px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider">Perfil</th>
						<th class="text-left px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider">Status</th>
						<th class="text-right px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider">Acoes</th>
					</tr>
				</thead>
				<tbody>
					{#each users as user}
						<tr class="border-b border-border-default last:border-0 hover:bg-bg-elevated/30 transition-colors">
							<td class="px-4 py-3">
								<div class="flex items-center gap-3">
									<div class="w-8 h-8 rounded-full bg-purple/10 text-[10px] font-bold text-purple flex items-center justify-center border border-purple/20 shrink-0">
										{user.iniciais}
									</div>
									<div>
										<p class="font-medium text-text-primary">{user.name}</p>
										<p class="text-xs text-text-muted">{user.email}</p>
									</div>
								</div>
							</td>
							<td class="px-4 py-3">
								<span class="px-2 py-0.5 rounded-full text-[11px] font-medium border {user.roleBadgeColor}">
									{user.roleLabel}
								</span>
							</td>
							<td class="px-4 py-3">
								{#if user.isActive}
									<span class="inline-flex items-center gap-1 text-xs text-green">
										<span class="w-1.5 h-1.5 rounded-full bg-green"></span>
										Ativo
									</span>
								{:else}
									<span class="inline-flex items-center gap-1 text-xs text-text-muted">
										<span class="w-1.5 h-1.5 rounded-full bg-gray-400"></span>
										Inativo
									</span>
								{/if}
							</td>
							<td class="px-4 py-3 text-right">
								<div class="flex items-center justify-end gap-1">
									<button
										data-testid="btn-editar-{user.id}"
										onclick={() => onEdit(user)}
										class="p-1.5 rounded-lg text-text-muted hover:text-purple hover:bg-purple/5 transition-all cursor-pointer"
										title="Editar"
									>
										<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
										</svg>
									</button>
									<button
										data-testid="btn-toggle-{user.id}"
										onclick={() => onToggleStatus(user)}
										class="p-1.5 rounded-lg transition-all cursor-pointer
											{user.isActive
												? 'text-text-muted hover:text-red hover:bg-red/5'
												: 'text-text-muted hover:text-green hover:bg-green/5'}"
										title={user.isActive ? 'Desativar' : 'Reativar'}
									>
										{#if user.isActive}
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
											</svg>
										{:else}
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
											</svg>
										{/if}
									</button>
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		{#if users.length === 0}
			<div class="text-center py-12">
				<p class="text-text-muted text-sm">Nenhum usuario encontrado.</p>
			</div>
		{/if}
	</div>
</div>
