# 786 Solution Spaceship frontend deployment

The website source is under `timer-html-master/`. The production target is the separately created `786solution.com` **FTP account root**, not the cPanel account home or KHAN Trading website folder.

## Status
- Dedicated cPanel FTPS account and Windows FTPS listing test: confirmed by account owner.
- GitHub Actions workflow: staged in PR #1; **no production deployment yet**.
- Existing `main`: unchanged by this addition.
- Domain A/CNAME still pointing to Vercel. Switch after the Spaceship site is tested.
- Contact FastAPI app: separate deployment, not included in this workflow.

## Before any deployment
1. In GitHub repository **Settings → Secrets and variables → Actions**, add these **repository secrets**:
   - `SPACESHIP_FTP_HOST`: `server37.shared.spaceship.host`
   - `SPACESHIP_FTP_USERNAME`: `786deploy@786solution.com`
   - `SPACESHIP_FTP_PASSWORD`: password chosen for that FTP account. **Do not put it in code, issues, PRs, screenshots, or chat.**
2. Confirm the FTP account is restricted to `/home/nwiyhfpyri/786solution.com/` only. Login as that account, not as the general cPanel account.
3. Review PR #1 and merge into `main` only when approved. The `workflow_dispatch` Run workflow button is available after the workflow file exists on the repository's **default branch**.
4. In **Settings → Secrets and variables → Actions → Variables**, create the repository variable `ENABLE_786_DEPLOY` with value `true` only when ready to allow deployment. With no variable or any other value, the job is skipped. Leave unset until reviewed and deployment desired.
5. In GitHub **Actions → Deploy 786 Solution frontend to Spaceship → Run workflow**, select `main`. Inspect logs for successful TLS connection and transferred assets. The action also automatically runs on future approved pushes to `main` affecting `timer-html-master/**` when the opt-in variable is true.
6. Verify index.html and image files exist in the separate Spaceship website root via cPanel File Manager. Test with an appropriate server preview or hosts-file approach before changing public DNS.
7. After confirming the site works on Spaceship, replace only the main-domain `@` A record and `www` CNAME at Hostinger. Keep existing `events`, `posdemo`, `smsdemo`, `salon`, and `hostel` A records unchanged.
8. Independently configure Spacemail MX, SPF, DKIM and the separate FastAPI contact backend. This workflow does not do those tasks.

## Safety
- FTPS encrypted control/data with valid server certificate required. If TLS fails, fix the certificate/server configuration; do not disable certificate validation.
- Deployment copies only the **contents** of `timer-html-master/` to the FTPS account root. Never point it at `/home/`, `public_html/` or another domain.
- No remote deletion by design; `.ftpquota` and unrelated server metadata are preserved. Obsolete site files must be reviewed and removed manually later.
- FTP credentials are not the previously generated SSH key and should not be exposed to pull-request workflows.
- Do not merge `main` before checking the work and the contact form's configured/unconfigured state.
