export function ShareModal({ playlistId, isOwnerOrAdmin, onClose, onUsersChanged = async () => {}, repo = null }) {
  const modalHtml = (
    <div id="share-modal" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="bg-neutral-900 border border-border rounded-lg p-8 max-w-md w-full flex flex-col gap-5">
        <h2 class="text-2xl font-bold text-foreground mb-4">Share Playlist</h2>

        <div class="flex gap-2 border-b border-border mb-2">
          <button id="tab-share" class="tab-btn pb-2 px-1 text-sm font-medium border-b-2 border-primary text-primary transition-colors">
            Share
          </button>
          <button id="tab-transfer" class="tab-btn pb-2 px-1 text-sm font-medium border-b-2 border-transparent text-muted-foreground hover:text-foreground transition-colors">
            Transfer ownership
          </button>
        </div>

        <div id="panel-share">
          <form id="share-form" class="flex flex-col gap-5">
            <div class="flex flex-col gap-5">
              <Input label="Email address" placeholder="vincent.berry@umontpellier.fr" id="email"/>
              <Input label="Is Editor?" id="editor" type="checkbox"/>
            </div>
            <div class="flex justify-end gap-4">
              <Button type="button" id="cancel-share" variant="secondary">Cancel</Button>
              <Button type="submit" id="submit-share" disabled>Share</Button>
            </div>
          </form>
        </div>

        <div id="panel-transfer" class="hidden flex flex-col gap-5">
          <p class="text-sm text-muted-foreground">
            Transfer ownership to another user.<br></br>
            <span class="text-destructive font-medium">This action is irreversible, you will lose access to this playlist unless the new owner invites you back.</span>
          </p>
          <form id="transfer-form" class="flex flex-col gap-5">
            <Input label="New owner email" placeholder="new.owner@umontpellier.fr" id="transfer-email"/>
            <div class="flex justify-end gap-4">
              <Button type="button" id="cancel-transfer" variant="secondary">Cancel</Button>
              <Button type="submit" id="submit-transfer" variant="destructive" disabled>Transfer</Button>
            </div>
          </form>
        </div>
          <div class="flex flex-col gap-2">
              <p class="text-sm font-semibold text-muted-foreground uppercase tracking-wider">People with access</p>
              <div id="shared-users-list" class="flex flex-col gap-2 max-h-64 overflow-y-auto">
                  <p class="text-sm text-muted-foreground">Loading...</p>
              </div>
          </div>
      </div>
    </div>
  );

  function render(container) {
      container.innerHTML = modalHtml;

      const tabShare = container.querySelector('#tab-share');
      const tabTransfer = container.querySelector('#tab-transfer');
      const panelShare = container.querySelector('#panel-share');
      const panelTransfer = container.querySelector('#panel-transfer');

      const usersList = container.querySelector('#shared-users-list');

      const playlistRepo = repo ?? new PlaylistRepository();

      function activateTab(tab) {
          const isShare = tab === 'share';
          tabShare.classList.toggle('border-primary', isShare);
          tabShare.classList.toggle('text-primary', isShare);
          tabShare.classList.toggle('border-transparent', !isShare);
          tabShare.classList.toggle('text-muted-foreground', !isShare);

          tabTransfer.classList.toggle('border-primary', !isShare);
          tabTransfer.classList.toggle('text-primary', !isShare);
          tabTransfer.classList.toggle('border-transparent', isShare);
          tabTransfer.classList.toggle('text-muted-foreground', isShare);

          panelShare.classList.toggle('hidden', !isShare);
          panelTransfer.classList.toggle('hidden', isShare);
      }

      tabShare.onclick = () => activateTab('share');
      tabTransfer.onclick = () => activateTab('transfer');

      const handleKeyDown = (e) => {
          if (e.key === 'Escape') cleanupAndClose();
      };
      const cleanupAndClose = () => {
          window.removeEventListener('keydown', handleKeyDown);
          onClose();
      };
      window.addEventListener('keydown', handleKeyDown);
      container.querySelector('#cancel-share').onclick = () => cleanupAndClose();

      const loadUsers = async () => {
          try {
              const users = await playlistRepo.sharedWith(playlistId);

              if (users.length === 0) {
                  usersList.innerHTML = `<p class="text-sm text-muted-foreground">No users have access yet.</p>`;
                  return;
              }

              usersList.innerHTML = users.map((u) => `
              <div class="flex items-center justify-between gap-3 px-3 py-2 rounded-lg bg-white/5 border border-white/8" data-user-id="${u.idUser}">
                <div class="flex items-center gap-3 min-w-0">
                  <div class="flex items-center justify-center w-9 h-9 rounded-full bg-neutral-700 text-sm font-semibold text-white shrink-0">
                    ${u.username.charAt(0).toUpperCase()}
                  </div>
                  <div class="min-w-0">
                    <p class="text-sm font-medium text-white truncate">${u.username}</p>
                    <p class="text-xs text-muted-foreground truncate">${u.email}</p>
                  </div>
                </div>
                <div class="flex items-center gap-2 shrink-0">
                  ${u.editor
                  ? `<span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/20">Editor</span>`
                  : `<span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-500/15 text-blue-400 border border-blue-500/20">Viewer</span>`
              }
                  ${isOwnerOrAdmin
                  ? `<button class="remove-user flex items-center justify-center w-7 h-7 rounded-lg text-red-400 hover:bg-red-500/10 transition-colors" data-user-id="${u.idUser}">✕</button>`
                  : ''
              }
                </div>
              </div>
            `).join('');

              if (isOwnerOrAdmin) {
                  usersList.querySelectorAll('.remove-user').forEach((btn: HTMLButtonElement) => {
                      btn.onclick = async () => {
                          const userId = Number(btn.getAttribute('data-user-id'));
                          btn.disabled = true;

                          try {
                              await playlistRepo.removeSharedUser(playlistId, userId);
                              const row = usersList.querySelector(`[data-user-id="${userId}"]`);
                              row?.remove();
                              if (usersList.children.length === 0) {
                                  usersList.innerHTML = `<p class="text-sm text-muted-foreground">No users have access yet.</p>`;
                              }
                              new AlertManager().success("User removed successfully");
                              await onUsersChanged();
                          } catch {
                              new AlertManager().error("Failed to remove user");
                              btn.disabled = false;
                          }
                      };
                  });
              }

          } catch {
              usersList.innerHTML = `<p class="text-sm text-red-400">Failed to load users.</p>`;
          }
      };

      loadUsers();

      if (isOwnerOrAdmin) {
          const emailInput = container.querySelector('#email');
          const editorInput = container.querySelector('#editor');
          const submitShare = container.querySelector('#submit-share');

          container.querySelector('#cancel-share').onclick = () => cleanupAndClose();

          let debounceTimer;
          emailInput.addEventListener('keyup', (e) => {
              clearTimeout(debounceTimer);
              debounceTimer = setTimeout(() => {
                  submitShare.disabled = !isValidEmail(e.target.value);
              }, 300);
          });

          container.querySelector('#share-form').onsubmit = async (e) => {
              e.preventDefault();
              const email = emailInput.value;
              const editor = container.querySelector('#editor').checked;
              const originalContent = submitShare.innerHTML;


              submitShare.disabled = true;
              submitShare.innerHTML = `
                  <svg class="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Sharing...`;

              try {
                  await new TrackRepository().share(playlistId, email, editor);
                  new AlertManager().success('Playlist shared successfully');
                  emailInput.value = '';
                  editorInput.checked = false;
                  submitShare.disabled = true;
                  playlistRepo.invalidateSharedWithCache(Number(playlistId));
                  await onUsersChanged();
                  await loadUsers();
                  cleanupAndClose();
              } catch {
                  submitShare.disabled = false;
                  submitShare.innerHTML = originalContent;
                  new AlertManager().error('Error sharing playlist');
              }
          };

          const transferEmailInput = container.querySelector('#transfer-email');
          const submitTransfer = container.querySelector('#submit-transfer');

          container.querySelector('#cancel-transfer').onclick = () => cleanupAndClose();

          let transferDebounce;
          transferEmailInput.addEventListener('keyup', (e) => {
              clearTimeout(transferDebounce);
              transferDebounce = setTimeout(() => {
                  submitTransfer.disabled = !isValidEmail(e.target.value);
              }, 500);
          });

          container.querySelector('#transfer-form').onsubmit = async (e) => {
              e.preventDefault();
              const email = transferEmailInput.value;
              const originalContent = submitTransfer.innerHTML;

              submitTransfer.disabled = true;

              try {
                  const response = await new PlaylistRepository().transfer_ownership(playlistId, email);
                  if (response === 200) {
                      window.location.href = '/playlists';
                      return;
                  }
                  throw new Error();
              } catch {
                  submitTransfer.disabled = false;
                  submitTransfer.innerHTML = originalContent;
                  new AlertManager().error('Error transferring ownership');
              }
          };
      }
  }

    return {render};
}
