import { AppBar, Toolbar, Typography, Box, IconButton } from "@mui/material";
import { GitHub, LinkedIn } from "@mui/icons-material";

export default function Footer() {
  return (
    <AppBar id="#contact" position="static" color="default" sx={{ mt: 0, py: 0 }}>
		  <Toolbar sx={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap" }}>
        
        {/* Left side: Personal note */}
        <Typography variant="body2" color="text.secondary">
          Made with ❤️ by Varun Gokte
        </Typography>

        {/* Right side: Contact info */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 2, mt: { xs: 1, sm: 0 } }}>
          <Typography variant="body2" color="text.secondary">
            📞 +91 9820468029
          </Typography>
          <Typography variant="body2" color="text.secondary">
            ✉️ vsgokte@gmail.com
          </Typography>
          <IconButton component="a" href="https://github.com/varun-gokte" target="_blank">
            <GitHub />
          </IconButton>
          <IconButton component="a" href="https://linkedin.com/in/varun-gokte" target="_blank">
            <LinkedIn />
          </IconButton>
        </Box>

      </Toolbar>
    </AppBar>
  );
}



