package org.vers.virus.immunity

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.View

/**
 * Initial view of the VirusImmunityPass app.
 */
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }

    fun openSelfTest(view: View) {
        startActivity(Intent(this, SelfTestActivity::class.java))
    }

    fun openShowStatus(view: View) {
        startActivity(Intent(this, ShowStatusActivity::class.java))
    }

    fun openChallengeStatus(view: View) {
        startActivity(Intent(this, ChallengeStatusActivity::class.java))
    }

}
